import time
import os
import logging
import hashlib
from multiprocessing import Process

from django.apps import AppConfig
from django.db.utils import OperationalError
from .gpx_converter import GPXConverter
from wizer.tools.utils import sanitize

log = logging.getLogger('wizer.apps')

sport_naming_map = {
    'Jogging': ['jogging', 'running'],
    'Cycling': ['cycle', 'cycling'],
    'Mountainbiking': ['mountainbiking', 'mountainbike', 'mountain biking', 'mountain bike', 'mountain-biking',
                       'mountain-bike', 'mtbing', 'mtb', 'cycling_mountain'],
    'Hiking': ['hiking', 'hike', 'wander', 'walking', 'mountaineering'],
    'Triathlon': ['triathlon', 'tria'],
}


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        from .models import Settings, TraceFiles, Activity, Sport
        try:
            # TODO get settings of current logged in user, maybe start GPXFileImporter only after login?
            settings = Settings.objects.all().order_by('-id').first()
            if settings:
                p = Process(target=GPXFileImporter, args=(settings, TraceFiles, Activity, Sport))
                p.start()
        except OperationalError:
            log.warning(f"could not find table: wizer_settgins - won't run GPXFileImprter. Run django migrations first.")
            # TODO create notification here


class GPXFileImporter:
    def __init__(self, settings_model, trace_files_model, activities_model, sport_model):
        self.settings = settings_model
        self.path = self.settings.path_to_trace_dir
        self.trace_files_model = trace_files_model
        self.activities_model = activities_model
        self.sport_model = sport_model
        self.interval = self.settings.gpx_checker_interval
        self.start_listening()

    def start_listening(self):
        while True:
            # find trace files in dir
            trace_files = [os.path.join(root, name)
                           for root, dirs, files in os.walk(self.path)
                           for name in files if name.endswith(".gpx")]
            log.debug(f"found {len(trace_files)} files in trace dir: {self.path}")
            self.add_objects_to_models(trace_files)
            time.sleep(self.interval)

    def add_objects_to_models(self, trace_files):
        md5sums_from_db = list(self.trace_files_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:   # current file is not stored in model yet
                log.debug(f"importing file {file}...")
                gjson = GPXConverter(path_to_gpx=file)
                sport = gjson.get_gpx_metadata().sport
                mapped_sport = map_sport_name(sport, sport_naming_map)
                t = self._save_gpx_file_to_db(file=file, md5sum=md5sum, geojson=gjson)
                trace_file_instance = self.trace_files_model.objects.get(pk=t.pk)
                sport_instance = self.sport_model.objects.filter(slug=sanitize(mapped_sport)).first()
                self._save_activity_to_db(geojson=gjson, sport=sport_instance, trace_file=trace_file_instance)
            else:  # means file is stored in db already
                trace_file_paths_model = self.trace_files_model.objects.get(md5sum=md5sum)
                if trace_file_paths_model.path_to_file != file:
                    log.debug(f"path of file: {trace_file_paths_model.path_to_file} has changed, updating to {file}")
                    trace_file_paths_model.path_to_file = file
                    trace_file_paths_model.save()

    def _save_gpx_file_to_db(self, file, md5sum, geojson):
        log.info(f"saving gpx file {file} to trace_files")
        gpx_metadata = geojson.get_gpx_metadata()
        t = self.trace_files_model(
            path_to_file=file,
            md5sum=md5sum,
            center_lon=gpx_metadata.center_lon,
            center_lat=gpx_metadata.center_lat,
            geojson=geojson.get_geojson(),
            zoom_level=gpx_metadata.zoom_level,
        )
        t.save()
        return t

    def _save_activity_to_db(self, geojson, sport, trace_file):
        gpx_metadata = geojson.get_gpx_metadata()
        title = gpx_metadata.title
        a = self.activities_model(
            title=title,
            sport=sport,
            date=gpx_metadata.date,
            duration=gpx_metadata.duration,
            distance=gpx_metadata.distance,
            trace_file=trace_file,
        )
        a.save()
        log.info(f"created new {sport} activity: {title}")
        return a


def map_sport_name(sport_name, map_dict):
    sport = None
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            log.debug(f"mapped activity sport: {sport_name} to {k}")
            sport = k
    if not sport:
        log.warning(f"could not map {sport_name} to given sport names, use None instead")
    return sport


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
