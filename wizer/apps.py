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
from wizer.file_helper.initial_data_handler import insert_settings_and_sports_to_model, \
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
            from wizer.models import Settings, Traces, Activity, Sport

            # if needed you can perform custom migrations here, see tools/migration_utils

            # insert initial example activity data in the case there is none
            if Activity.objects.count() == 0:
                insert_settings_and_sports_to_model(
                    settings_model=Settings,
                    sport_model=Sport)
                create_initial_trace_data_with_recent_time()
                insert_activities_to_model(
                    sport_model=Sport,
                    activity_model=Activity)
                log.info(f"inserting initial example data done.")
            fi = Process(target=FileImporter, args=(Settings, Traces, Activity, Sport))
            fi.start()


class FileImporter:
    def __init__(self, settings_model, traces_model, activities_model, sport_model):
        self.settings = settings_model.objects.get(pk=1)
        self.traces_model = traces_model
        self.activities_model = activities_model
        self.sport_model = sport_model
        self._start_listening()

    def _start_listening(self):
        try:
            fit_collector = FitCollector(
                path_to_garmin_device=self.settings.path_to_garmin_device,
                target_location=self.settings.path_to_trace_dir,
                delete_files_after_import=self.settings.delete_files_after_import,
            )
            while True:
                fit_collector.copy_fit_files()
                path = self.settings.path_to_trace_dir
                interval = self.settings.file_checker_interval
                # find activity files in directory
                trace_files = get_all_files(path)
                if os.path.isdir(path):
                    log.debug(f"found {len(trace_files)} files in trace dir: {path}")
                    self._run_parser(trace_files)
                else:
                    log.warning(f"path: {path} is not a valid directory!")
                    break
                time.sleep(interval)
        except OperationalError as e:
            log.debug(f"cannot run FileImporter. Maybe run django migrations first: {e}")

    def _run_parser(self, trace_files):
        md5sums_from_db = get_md5sums_from_model(traces_model=self.traces_model)
        for trace_file in trace_files:
            md5sum = calc_md5(trace_file)
            if md5sum not in md5sums_from_db:  # current file is not stored in model yet
                try:
                    trace_file_instance = parse_and_save_to_model(
                        traces_model=self.traces_model,
                        activity_model=self.activities_model,
                        sport_model=self.sport_model,
                        md5sum=md5sum,
                        trace_file=trace_file)
                except Exception as e:
                    log.error(f"could not import activity of file: {trace_file}. {e}", exc_info=True)
                    # It might be the case, that the trace file object was created, but no activity.
                    # Delete the trace file object again, to enable reimporting
                    try:
                        log.debug(f"removed {trace_file_instance} from model, since activity was not created")
                        trace_file_instance.delete()
                    except Exception as e:
                        log.debug(f"could not delete trace file object, since it was not created yet, {e}")
            else:  # checksum is in db already
                file_name = trace_file.split("/")[-1]
                trace_file_path_instance = self.traces_model.objects.get(md5sum=md5sum)
                if trace_file_path_instance.file_name == file_name and trace_file_path_instance.path_to_file != trace_file:
                    log.debug(
                        f"path of file: {trace_file_path_instance.path_to_file} has changed, updating to {trace_file}")
                    trace_file_path_instance.path_to_file = trace_file
                    trace_file_path_instance.save()
                elif trace_file_path_instance.file_name != file_name and trace_file_path_instance.path_to_file != trace_file:
                    log.warning(f"The following two files have the same checksum, "
                                f"you might want to remove one of them:\n"
                                f"{trace_file}\n"
                                f"{trace_file_path_instance.path_to_file}")
                else:
                    pass  # means file is already in db


def parse_and_save_to_model(traces_model, sport_model, activity_model, md5sum, trace_file):
    parser = parse_activity_data(trace_file)
    trace_file_object = _save_to_trace_model(
        traces_model=traces_model, md5sum=md5sum,
        parser=parser, trace_file=trace_file)
    trace_file_instance = traces_model.objects.get(pk=trace_file_object.pk)
    sport = parser.sport
    mapped_sport = map_sport_name(sport, sport_naming_map)
    sport_instance = sport_model.objects.filter(slug=sanitize(mapped_sport)).first()
    _save_to_activity_model(
        activities_model=activity_model, parser=parser,
        sport_instance=sport_instance, trace_file_instance=trace_file_instance)
    log.info(f"created new {sport_instance} activity: {parser.file_name}")
    return trace_file_instance


def _save_to_activity_model(activities_model, parser, sport_instance, trace_file_instance):
    activity_object = activities_model(
        name=parser.file_name.replace(".gpx", "").replace(".fit", ""),
        sport=sport_instance,
        date=parser.date,
        duration=parser.duration,
        distance=parser.distance,
        trace_file=trace_file_instance,
    )
    activity_object.save()


def _save_to_trace_model(traces_model, md5sum, parser, trace_file):
    log.debug(f"saving trace file {trace_file} to traces model")
    trace_object = traces_model(
        path_to_file=trace_file,
        md5sum=md5sum,
        coordinates_list=parser.coordinates_list,
        altitude_list=parser.altitude_list,
        calories=parser.calories,
        # heart rate
        heart_rate_list=parser.heart_rate_list,
        min_heart_rate=parser.min_heart_rate,
        avg_heart_rate=parser.avg_heart_rate,
        max_heart_rate=parser.max_heart_rate,
        # cadence
        cadence_list=parser.cadence_list,
        min_cadence=parser.min_cadence,
        avg_cadence=parser.avg_cadence,
        max_cadence=parser.max_cadence,
        # speed
        speed_list=parser.speed_list,
        min_speed=parser.min_speed,
        avg_speed=parser.avg_speed,
        max_speed=parser.max_speed,
        # temperature
        temperature_list=parser.temperature_list,
        min_temperature=parser.min_temperature,
        avg_temperature=parser.avg_temperature,
        max_temperature=parser.max_temperature,
        # training effect
        aerobic_training_effect=parser.aerobic_training_effect,
        anaerobic_training_effect=parser.anaerobic_training_effect,
        # timestamps
        timestamps_list=parser.timestamps_list,
    )
    trace_object.save()
    return trace_object


def get_md5sums_from_model(traces_model):
    md5sums_from_db = list(traces_model.objects.all())
    md5sums_from_db = [m.md5sum for m in md5sums_from_db]
    return md5sums_from_db


def parse_activity_data(file):
    log.debug(f"importing file {file} ...")
    if file.endswith(".gpx"):
        log.debug(f"parsing GPX file ...")
        parser = GPXParser(path_to_file=file)
    elif file.endswith(".fit"):
        log.debug(f"parsing FIT file ...")
        parser = FITParser(path_to_file=file)
        parser.convert_list_of_nones_to_empty_list()
        parser.set_min_max_values()
        parser.convert_list_attributes_to_json()
    else:
        log.warning(f"file type: {file} unknown")
        parser = None
    return parser


def map_sport_name(sport_name, map_dict):
    sport = 'unknown'
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            log.debug(f"mapped activity sport: {sport_name} to {k}")
            sport = k
    if not sport:
        log.warning(f"could not map {sport_name} to given sport names, use unknown instead")
    return sport


def get_all_files(path):
    trace_files = [os.path.join(root, name)
                   for root, dirs, files in os.walk(path)
                   for name in files if name.endswith(tuple(formats))]
    return trace_files
