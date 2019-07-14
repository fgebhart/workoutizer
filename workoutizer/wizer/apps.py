import time
import os
import logging
import hashlib
from multiprocessing import Process

from django.apps import AppConfig
from django.db.utils import OperationalError
from .gpx_converter import GPXConverter
from .tools import sanitize

log = logging.getLogger('wizer.apps')

sport_map = {
    'Jogging': ['jogging', 'running'],
    'Mountainbiking': ['mountainbiking', 'mountainbike', 'mountain biking', 'mountain bike', 'mountain-biking',
                       'mountain-bike', 'mtbing', 'mtb'],
    'Hiking': ['hiking', 'hike', 'wander', 'walking', 'mountaineering'],
}


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        from .models import Settings, TraceFiles, Activity, Sport
        try:
            settings = Settings.objects.all().order_by('-id').first()
            if settings:
                p = Process(target=GPXFileImporter, args=(settings.path_to_trace_dir, TraceFiles, Activity, Sport))
                p.start()
        except OperationalError:
            log.warning(f"could not find table: wizer_settgins - won't run GPXFileImprter. Run django migrations first.")


class GPXFileImporter:
    def __init__(self, path, trace_files_model, activities_model, sport_model):
        self.path = path
        self.trace_files_model = trace_files_model
        self.activities_model = activities_model
        self.sport_model = sport_model
        self.start_listening()

    def start_listening(self):
        while True:
            # find trace files in dir
            trace_files = [os.path.join(root, name)
                           for root, dirs, files in os.walk(self.path)
                           for name in files if name.endswith(".gpx")]
            log.debug(f"found {len(trace_files)} files in trace dir: {self.path}")
            self.add_objects_to_models(trace_files)

            time.sleep(3)

    def add_objects_to_models(self, trace_files):
        md5sums_from_db = list(self.trace_files_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:   # current file is not stored in model yet
                gjson = GPXConverter(path_to_gpx=file)
                mapped_sport = map_sport_name(gjson.get_gpx_metadata().sport, sport_map)
                t = self._save_gpx_file_to_db(file=file, md5sum=md5sum, geojson=gjson)
                trace_file_instance = self.trace_files_model.objects.get(pk=t.pk)
                sport_instance = self.sport_model.objects.get(slug=sanitize(mapped_sport))
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
        a = self.activities_model(
            title=gpx_metadata.title,
            sport=sport,
            date=gpx_metadata.date,
            duration=gpx_metadata.duration,
            distance=gpx_metadata.distance,
            trace_file=trace_file,
        )
        a.save()
        return a


def map_sport_name(sport_name, map_dict):
    sport = "other"
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            log.debug(f"mapped activity sport: {sport_name} to {k}")
            sport = k
    return sport


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
