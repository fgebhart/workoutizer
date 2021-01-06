import os
import sys
import logging
import json
from typing import List


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from django.apps import AppConfig
from django.db.utils import OperationalError

from wizer.file_helper.gpx_parser import GPXParser
from wizer.file_helper.fit_parser import FITParser
from wizer.file_helper.auto_naming import get_automatic_name
from wizer.tools.utils import sanitize, calc_md5
from wizer.file_helper.initial_data_handler import (
    copy_demo_fit_files_to_track_dir,
    change_date_of_demo_activities,
    insert_demo_sports_to_model,
    insert_custom_demo_activities,
)
from wizer.configuration import supported_formats
from workoutizer import settings as django_settings


log = logging.getLogger(__name__)

sport_naming_map = {
    "Jogging": ["jogging", "running"],
    "Cycling": ["cycle", "cycling", "biking"],
    "Mountainbiking": [
        "mountainbiking",
        "mountainbike",
        "mountain biking",
        "mountain bike",
        "mountain-biking",
        "mountain-bike",
        "mtbing",
        "mtb",
        "cycling_mountain",
    ],
    "Hiking": ["hiking", "hike", "wandern", "walking", "mountaineering"],
    "Triathlon": ["triathlon", "tria"],
    "Swimming": ["swimming", "swim", "pool"],
    "Yoga": ["yoga", "yogi"],
    "Workout": ["training"],
}


def _was_runserver_triggered(args: list):
    triggered = False
    if "run" in args:
        triggered = True
    if "runserver" in args:
        triggered = True
    if "help" in args:
        triggered = False
    if "--help" in args:
        triggered = False

    return triggered


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.event_type == "created":
            if str(event.src_path).endswith(".fit") or str(event.src_path).endswith(".gpx"):
                log.debug("activity file was added, triggering FileImporter...")

                from wizer import models

                FileImporter(models, importing_demo_data=False)


class WizerFileDaemon(AppConfig):
    name = "wizer"

    def ready(self):
        # ensure to only run with 'manage.py runserver' and not in auto reload thread
        if _was_runserver_triggered(sys.argv) and os.environ.get("RUN_MAIN", None) != "true":
            log.info(f"using workoutizer home at {django_settings.WORKOUTIZER_DIR}")
            from wizer import models

            FileImporter(models, importing_demo_data=False)

            _start_watchdog(path=django_settings.TRACKS_DIR)


def _start_watchdog(path: str):
    event_handler = Handler()
    watchdog = Observer()
    watchdog.schedule(event_handler, path=path, recursive=True)
    watchdog.start()
    log.debug(f"started watchdog to watch for incoming files in {path}")


def prepare_import_of_demo_activities(models, list_of_files_to_copy: list = []):
    models.get_settings()
    insert_demo_sports_to_model(models)
    copy_demo_fit_files_to_track_dir(
        source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
        targe_dir=models.get_settings().path_to_trace_dir,
        list_of_files_to_copy=list_of_files_to_copy,
    )


class FileImporter:
    def __init__(self, models, importing_demo_data):
        self.importing_demo_data = importing_demo_data
        self.settings = models.get_settings()
        self.models = models
        log.debug("triggered file importer")
        self._run_importer()

    def _run_importer(self):
        try:
            path = self.settings.path_to_trace_dir
            # find activity files in directory
            trace_files = get_all_files(path)
            if os.path.isdir(path):
                log.info(f"found {len(trace_files)} files in trace dir: {path}")
                run_parser(self.models, trace_files, self.importing_demo_data)
            else:
                log.error(f"path: {path} is not a valid directory!")
                return
            if self.importing_demo_data:
                demo_activities = self.models.Activity.objects.filter(is_demo_activity=True)
                change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)
                insert_custom_demo_activities(
                    count=9, every_nth_day=3, activity_model=self.models.Activity, sport_model=self.models.Sport
                )
                log.info("finished inserting demo data")
                self.importing_demo_data = False
        except OperationalError as e:
            log.warning(f"cannot run FileImporter. Maybe run django migrations first: {e}")


def run_parser(models, trace_files: list, importing_demo_data: bool):
    md5sums_from_db = get_md5sums_from_model(traces_model=models.Traces)
    for trace_file in trace_files:
        md5sum = calc_md5(trace_file)
        if md5sum not in md5sums_from_db:  # current file is not stored in model yet
            try:
                trace_file_instance = parse_and_save_to_model(
                    models=models,
                    md5sum=md5sum,
                    trace_file=trace_file,
                    importing_demo_data=importing_demo_data,
                )
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
            trace_file_path_instance = models.Traces.objects.get(md5sum=md5sum)
            if trace_file_path_instance.file_name == file_name and trace_file_path_instance.path_to_file != trace_file:
                log.debug(f"path of file: {trace_file_path_instance.path_to_file} has changed, updating to {trace_file}")
                trace_file_path_instance.path_to_file = trace_file
                trace_file_path_instance.save()
            elif trace_file_path_instance.file_name != file_name and trace_file_path_instance.path_to_file != trace_file:
                log.warning(
                    f"The following two files have the same checksum, "
                    f"you might want to remove one of them:\n"
                    f"{trace_file}\n"
                    f"{trace_file_path_instance.path_to_file}"
                )
            else:
                pass  # means file is already in db


def parse_and_save_to_model(models, md5sum, trace_file, importing_demo_data=False):
    parser = parse_data(trace_file)
    trace_file_object = _save_trace_to_model(
        traces_model=models.Traces, md5sum=md5sum, parser=parser, trace_file=trace_file
    )
    trace_file_instance = models.Traces.objects.get(pk=trace_file_object.pk)
    sport = parser.sport
    mapped_sport = map_sport_name(sport, sport_naming_map)
    sport_instance = models.Sport.objects.filter(slug=sanitize(mapped_sport)).first()
    if sport_instance is None:  # needs to be adapted in GH #4
        sport_instance = models.default_sport(return_pk=False)
    save_laps_to_model(
        lap_model=models.Lap,
        laps=parser.laps,
        trace_instance=trace_file_instance,
    )
    setattr(parser, "activity_name", get_automatic_name(parser, sport))
    activity_object = _save_activity_to_model(
        activities_model=models.Activity,
        parser=parser,
        sport_instance=sport_instance,
        trace_instance=trace_file_instance,
        importing_demo_data=importing_demo_data,
    )
    activity_instace = models.Activity.objects.get(pk=activity_object.pk)
    save_best_sections_to_model(best_section_model=models.BestSection, parser=parser, activity_instance=activity_instace)
    log.info(f"created new {sport_instance} activity: '{parser.activity_name}'. ID: {activity_object.pk}")
    return trace_file_instance


def save_laps_to_model(lap_model, laps: list, trace_instance):
    for lap in laps:
        lap_object = lap_model(
            start_time=lap.start_time,
            end_time=lap.end_time,
            elapsed_time=lap.elapsed_time,
            trigger=lap.trigger,
            start_lat=lap.start_lat,
            start_long=lap.start_long,
            end_lat=lap.end_lat,
            end_long=lap.end_long,
            distance=lap.distance,
            speed=lap.speed,
            trace=trace_instance,
        )
        lap_object.save()


def save_best_sections_to_model(best_section_model, parser, activity_instance):
    # save fastest sections to model
    for section in parser.best_sections:
        best_section_object = best_section_model(
            activity=activity_instance,
            section_type=section.section_type,
            section_distance=section.section_distance,
            start_index=section.start_index,
            end_index=section.end_index,
            max_value=section.velocity,
        )
        best_section_object.save()
    # save also other section types to model here...


def _save_activity_to_model(activities_model, parser, sport_instance, trace_instance, importing_demo_data):
    activity_object = activities_model(
        name=parser.activity_name,
        sport=sport_instance,
        date=parser.date,
        duration=parser.duration,
        distance=parser.distance,
        trace_file=trace_instance,
        is_demo_activity=importing_demo_data,
    )
    activity_object.save()
    return activity_object


def _save_trace_to_model(traces_model, md5sum, parser, trace_file):
    log.debug(f"saving trace file {trace_file} to traces model")
    parser = convert_list_attributes_to_json(parser)
    trace_object = traces_model(
        path_to_file=trace_file,
        md5sum=md5sum,
        calories=parser.calories,
        # coordinates
        latitude_list=parser.latitude_list,
        longitude_list=parser.longitude_list,
        # distances
        distance_list=parser.distance_list,
        # altitude
        altitude_list=parser.altitude_list,
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


def convert_list_attributes_to_json(parser):
    for attribute, values in parser.__dict__.items():
        if attribute.endswith("_list"):
            setattr(parser, attribute, json.dumps(values))
    return parser


def get_md5sums_from_model(traces_model):
    md5sums_from_db = list(traces_model.objects.all())
    md5sums_from_db = [m.md5sum for m in md5sums_from_db]
    return md5sums_from_db


def parse_data(file):
    log.debug(f"importing file {file} ...")
    if file.endswith(".gpx"):
        log.debug("parsing GPX file ...")
        parser = GPXParser(path_to_file=file)
    elif file.endswith(".fit"):
        log.debug("parsing FIT file ...")
        parser = FITParser(path_to_file=file)
        parser.convert_list_of_nones_to_empty_list()
        parser.set_min_max_values()
    else:
        log.error(f"file type: {file} unknown")
        raise NotImplementedError(f"Cannot parse {file} files. Only {supported_formats} are supported.")
    # parse best sections
    parser.get_fastest_sections()
    return parser


def map_sport_name(sport_name, map_dict):  # will be adapted in GH #4
    sport = None
    for k, v in map_dict.items():
        if sanitize(sport_name) in v:
            sport = k
    if sport:
        log.debug(f"mapped activity sport: {sport_name} to {sport}")
    else:
        sport = "unknown"
        log.warning(f"could not map '{sport_name}' to given sport names, use unknown instead")
    return sport


def get_all_files(path) -> List[str]:
    trace_files = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(path)
        for name in files
        if name.endswith(tuple(supported_formats))
    ]
    return trace_files
