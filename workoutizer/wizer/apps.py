import time
import os
import logging
import hashlib
from multiprocessing import Process

from django.apps import AppConfig
from .gpx_converter import GPXConverter
from .tools import sanitize

log = logging.getLogger('wizer.apps')


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        from .models import Settings, TraceFiles, Activity, Sport
        settings = Settings.objects.all().order_by('-id').first()
        if settings:
            p = Process(target=FileChecker, args=(settings.path_to_trace_dir, TraceFiles, Activity, Sport))
            p.start()


class FileChecker:
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
            log.debug(f"found files in trace dir: {trace_files}")
            self.save_files_to_db(trace_files)

            time.sleep(100)

    def save_files_to_db(self, trace_files):
        md5sums_from_db = list(self.trace_files_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:
                log.info(f"adding file {file} to db")
                gjson = GPXConverter(path_to_gpx=file)
                gpx_metadata = gjson.get_gpx_metadata()
                t = self.trace_files_model(
                    path_to_file=file,
                    md5sum=md5sum,
                    center_lon=gpx_metadata.center_lon,
                    center_lat=gpx_metadata.center_lat,
                    geojson=gjson.get_geojson(),
                    zoom_level=gpx_metadata.zoom_level,
                )
                t.save()
                trace_files_instance = self.trace_files_model.objects.get(pk=t.pk)
                sport_instance = self.sport_model.objects.get(slug=sanitize(gpx_metadata.sport))
                a = self.activities_model(
                    title=gpx_metadata.title,
                    sport=sport_instance,
                    date=gpx_metadata.date,
                    duration=gpx_metadata.duration,
                    distance=gpx_metadata.distance,  # TODO not yet implemented - calculate total distance from gpx file
                    trace_file=trace_files_instance,
                )
                a.save()
            else:   # means file is referenced in db already
                trace_file_paths_model = self.trace_files_model.objects.get(md5sum=md5sum)
                if trace_file_paths_model.path_to_file != file:
                    log.debug(f"path of file: {trace_file_paths_model.path_to_file} has changed, updating to {file}")
                    trace_file_paths_model.path_to_file = file
                    trace_file_paths_model.save()


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
