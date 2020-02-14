import time
import os
import sys
import logging
from multiprocessing import Process

from django.apps import AppConfig
from django.db.utils import OperationalError

from wizer.file_helper.gpx_parser import GPXParser
from wizer.file_helper.fit_parser import FITParser
from wizer.file_helper.fit_collector import FitCollector
from wizer.tools.utils import sanitize, calc_md5
from wizer.tools.initial_trace_data_handler import insert_settings_and_sports_to_model, \
    create_initial_trace_data_with_recent_time, insert_activities_to_model

log = logging.getLogger(__name__)

sport_naming_map = {
    'Jogging': ['jogging', 'running'],
    'Cycling': ['cycle', 'cycling', 'biking'],
    'Mountainbiking': ['mountainbiking', 'mountainbike', 'mountain biking', 'mountain bike', 'mountain-biking',
                       'mountain-bike', 'mtbing', 'mtb', 'cycling_mountain'],
    'Hiking': ['hiking', 'hike', 'wandern', 'walking', 'mountaineering'],
    'Triathlon': ['triathlon', 'tria'],
    'Swimming': ['swimming', 'swim', 'pool'],
    'Yoga': ['yoga', 'yogi'],
    'Workout': ['training'],
}

formats = [".gpx", ".fit"]


class WizerFileDaemon(AppConfig):
    name = 'wizer'
    verbose_name = 'Workoutizer'

    def ready(self):
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN', None) != 'true':
            # ensure to only run with 'manage.py runserver' and not in auto reload thread
            from .models import Settings, Traces, Activity, Sport

            # ensure all trace objects have the min and max altitude value
            # from wizer.tools.migration_utils.migrate_altitudes import migrate_altitudes
            # migrate_altitudes(Traces)

            if os.environ.get('DEVENV') == 'docker':
                insert_settings_and_sports_to_model(
                    settings_model=Settings,
                    sport_model=Sport)
                create_initial_trace_data_with_recent_time()
                insert_activities_to_model(
                    sport_model=Sport,
                    activity_model=Activity)
            fi = Process(target=FileImporter, args=(Settings, Traces, Activity, Sport))
            fi.start()


class FileImporter:
    def __init__(self, settings_model, traces_model, activities_model, sport_model):
        self.settings = settings_model
        self.traces_model = traces_model
        self.activities_model = activities_model
        self.sport_model = sport_model
        self.start_listening()

    def start_listening(self):
        try:
            fit_collector = FitCollector(settings_model=self.settings)
            while True:
                fit_collector.look_for_fit_files()
                settings = self.settings.objects.get(pk=1)
                path = settings.path_to_trace_dir
                interval = settings.file_checker_interval
                # find activity files in directory
                trace_files = [os.path.join(root, name)
                               for root, dirs, files in os.walk(path)
                               for name in files if name.endswith(tuple(formats))]
                if os.path.isdir(path):
                    log.debug(f"found {len(trace_files)} files in trace dir: {path}")
                    self.add_objects_to_models(trace_files)
                else:
                    log.warning(f"path: {path} is not a valid directory!")
                    break
                time.sleep(interval)
        except OperationalError as e:
            log.debug(f"cannot run FileImporter. Run django migrations first: {e}")

    def add_objects_to_models(self, trace_files):
        md5sums_from_db = list(self.traces_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:  # current file is not stored in model yet
                try:
                    log.debug(f"importing file {file}...")
                    if file.endswith(".gpx"):
                        log.debug(f"parsing GPX file")
                        parser = GPXParser(path_to_file=file)
                    elif file.endswith(".fit"):
                        log.debug(f"parsing FIT file")
                        parser = FITParser(path_to_file=file)
                        parser.parse_heart_rate()
                        parser.parse_calories()
                    else:
                        log.warning(f"file type: {file} unknown")
                        parser = None
                    sport = parser.sport
                    mapped_sport = map_sport_name(sport, sport_naming_map)
                    log.debug(f"saving trace file {file} to traces model")
                    t = self.traces_model(
                        path_to_file=file,
                        md5sum=md5sum,
                        coordinates=parser.coordinates,
                        elevation=parser.elevation,
                        heart_rate=parser.heart_rate,
                    )
                    t.save()
                    trace_file_instance = self.traces_model.objects.get(pk=t.pk)
                    sport_instance = self.sport_model.objects.filter(slug=sanitize(mapped_sport)).first()
                    a = self.activities_model(
                        name=parser.name,
                        sport=sport_instance,
                        date=parser.date,
                        duration=parser.duration,
                        distance=parser.distance,
                        trace_file=trace_file_instance,
                        calories=parser.calories,
                    )
                    a.save()
                    log.info(f"created new {sport_instance} activity: {parser.name}")
                except Exception as e:
                    log.error(f"could not import activity of file: {file}. {e}", exc_info=True)
            else:  # means file is stored in db already
                trace_file_path_instance = self.traces_model.objects.get(md5sum=md5sum)
                if trace_file_path_instance.path_to_file != file:
                    log.debug(f"path of file: {trace_file_path_instance.path_to_file} has changed, updating to {file}")
                    trace_file_path_instance.path_to_file = file
                    trace_file_path_instance.save()


def map_sport_name(sport_name, map_dict):
    sport = None
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            log.debug(f"mapped activity sport: {sport_name} to {k}")
            sport = k
    if not sport:
        log.warning(f"could not map {sport_name} to given sport names, use None instead")
    return sport
