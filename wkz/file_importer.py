import os
import logging
import json
from pathlib import Path
from typing import List, Union
from types import ModuleType

from fitparse.utils import FitHeaderError, FitEOFError
import dask
from dask.delayed import Delayed

from wkz.file_helper.parser import Parser
from wkz.file_helper.gpx_parser import GPXParser
from wkz.file_helper.fit_parser import FITParser
from wkz.file_helper.auto_naming import get_automatic_name
from wkz.tools.utils import sanitize, calc_md5, limit_string
from wkz.tools import sse
from wkz.file_helper.initial_data_handler import (
    copy_demo_fit_files_to_track_dir,
    change_date_of_demo_activities,
    insert_demo_sports_to_model,
    insert_custom_demo_activities,
)
from wkz.best_sections.generic import GenericBestSection
from wkz import configuration
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


def prepare_import_of_demo_activities(models, list_of_files_to_copy: list = []):
    settings = models.get_settings()
    insert_demo_sports_to_model(models)
    copy_demo_fit_files_to_track_dir(
        source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
        targe_dir=settings.path_to_trace_dir,
        list_of_files_to_copy=list_of_files_to_copy,
    )


def _send_initial_info(number_of_activities: int, path_to_trace_dir: str, reimporting: bool):
    if reimporting:
        what_is_done = "Reimport"
    else:
        what_is_done = "File Import"
    if number_of_activities > 0:
        sse.send(
            f"<b>{what_is_done} started:</b> Found {number_of_activities} activity files in "
            f"<code>{path_to_trace_dir}</code>. Please wait.",
            "blue",
        )
    else:
        sse.send(f"No new activity files found in <code>{path_to_trace_dir}</code>.", "green")


def _parse_and_save_to_model(
    models, md5sum: str, trace_file: Path, update_existing: bool, importing_demo_data: bool = False
):
    # run actual file parser
    parser = _parse_data(trace_file, md5sum)
    # save trace data to model
    trace_file_object = _save_trace_to_model(
        traces_model=models.Traces,
        md5sum=md5sum,
        parser=parser,
        trace_file=trace_file,
        update_existing=update_existing,
    )
    trace_file_instance = models.Traces.objects.get(pk=trace_file_object.pk)
    # save laps to model
    _save_laps_to_model(
        lap_model=models.Lap, laps=parser.laps, trace_instance=trace_file_instance, update_existing=update_existing
    )
    # save activity itself to model
    activity_object = _save_activity_to_model(
        models=models,
        parser=parser,
        trace_instance=trace_file_instance,
        importing_demo_data=importing_demo_data,
        update_existing=update_existing,
    )
    activity_instance = models.Activity.objects.get(pk=activity_object.pk)
    # save best sections to model
    _save_best_sections_to_model(
        best_section_model=models.BestSection,
        parser=parser,
        activity_instance=activity_instance,
        update_existing=update_existing,
    )
    return activity_instance


def _save_laps_to_model(lap_model, laps: list, trace_instance, update_existing: bool):
    if update_existing:
        for lap in laps:
            lap_model.objects.update_or_create(
                trace=trace_instance,
                start_time=lap.start_time,
                end_time=lap.end_time,
                elapsed_time=lap.elapsed_time,
                trigger=lap.trigger,
                start_lat=lap.start_lat,
                start_long=lap.start_long,
                end_lat=lap.end_lat,
                end_long=lap.end_long,
                distance=lap.distance,
                defaults={"speed": lap.speed},  # only speed could really be updated
            )
    else:
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


def _save_best_sections_to_model(best_section_model, parser, activity_instance, update_existing: bool):
    if update_existing:
        log.debug(f"updating best sections for: {activity_instance.name}")
        for section in parser.best_sections:
            best_section_model.objects.update_or_create(
                activity=activity_instance,
                kind=section.kind,
                distance=section.distance,
                defaults={
                    "start": section.start,
                    "end": section.end,
                    "max_value": section.max_value,
                },
            )
        # If the parser does not have some best sections but the db has -> delete them from the db
        db_sections = best_section_model.objects.filter(activity=activity_instance)
        for section in db_sections:
            sec = GenericBestSection(section.distance, section.start, section.end, section.max_value, section.kind)
            if sec not in parser.best_sections:
                log.debug(f"deleting section: {section} from db, because it is not present in parser")
                section.delete()
    else:
        # save best sections to model
        for section in parser.best_sections:
            best_section_object = best_section_model(
                activity=activity_instance,
                kind=section.kind,
                distance=section.distance,
                start=section.start,
                end=section.end,
                max_value=section.max_value,
            )
            best_section_object.save()


def _map_sport_name(sport_name, map_dict):  # will be adapted in GH #4
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


def _save_activity_to_model(models, parser, trace_instance, importing_demo_data: bool, update_existing: bool):
    if update_existing:
        # name should not be overwritten
        activity_object = models.Activity.objects.get(trace_file=trace_instance)
        log.debug(f"updating activity attributes for: '{activity_object.name}'")
        activity_object.duration = parser.duration
        activity_object.distance = parser.distance
        if activity_object.is_demo_activity:
            log.debug(f"won't update date of demo activity: '{activity_object.name}' (ID: {activity_object.pk})")
        else:
            log.debug(f"updating date of non-demo activity: '{activity_object.name}' (ID: {activity_object.pk})")
            activity_object.date = parser.date
    else:
        # get appropriate sport from db
        sport = parser.sport
        mapped_sport = _map_sport_name(sport, sport_naming_map)
        sport_instance = models.Sport.objects.filter(slug=sanitize(mapped_sport)).first()
        if sport_instance is None:  # needs to be adapted in GH #4
            sport_instance = models.default_sport(return_pk=False)
        # determine automatic name (based on location and daytime)
        activity_object = models.Activity(
            name=get_automatic_name(parser, mapped_sport),
            sport=sport_instance,
            date=parser.date,
            duration=parser.duration,
            distance=parser.distance,
            trace_file=trace_instance,
            is_demo_activity=importing_demo_data,
        )
    activity_object.save()
    return activity_object


def _save_trace_to_model(traces_model, md5sum: str, parser, trace_file, update_existing: bool):
    parser = _convert_list_attributes_to_json(parser)
    if update_existing:
        trace_object = traces_model.objects.get(md5sum=md5sum)
        for attribute, value in parser.__dict__.items():
            if attribute == "sport":
                continue
            if hasattr(trace_object, attribute):
                db_value = getattr(trace_object, attribute)
                log.debug(
                    f"overwriting value for {attribute} old: {limit_string(db_value, 50)} "
                    f"to: {limit_string(value, 50)}"
                )
                setattr(trace_object, attribute, value)
    else:
        log.debug(f"saving trace file {trace_file} to traces model")
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
            max_altitude=parser.max_altitude,
            min_altitude=parser.min_altitude,
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


def _convert_list_attributes_to_json(parser):
    for attribute, values in parser.__dict__.items():
        if attribute.endswith("_list"):
            setattr(parser, attribute, json.dumps(values))
    return parser


def _get_md5sums_from_model(traces_model) -> List[str]:
    return list(traces_model.objects.all().values_list("md5sum", flat=True))


def _parse_data(file: Path, md5sum: str) -> Union[FITParser, GPXParser]:
    file = str(file)
    log.debug(f"importing file {file} ...")
    if file.endswith(".gpx"):
        log.debug("parsing GPX file ...")
        parser = GPXParser(path_to_file=file, md5sum=md5sum)
    elif file.endswith(".fit"):
        log.debug("parsing FIT file ...")
        parser = FITParser(path_to_file=file, md5sum=md5sum)
    else:
        log.error(f"file type: {file} unknown")
        raise NotImplementedError(
            f"Cannot parse {file} files. The only supported file formats are: {configuration.supported_formats}."
        )
    # parse best sections
    parser.get_best_sections()
    log.debug(f"finished parsing file {file}.")
    return parser


def _get_all_files(path: Path) -> List[Path]:
    trace_files = [
        Path(os.path.join(root, name))
        for root, dirs, files in os.walk(path)
        for name in files
        if name.endswith(tuple(configuration.supported_formats))
    ]
    return trace_files


def _parse_single_file(
    path_to_file: Path,
    md5sum: str,
    path_to_traces: Path,
    inform_about_nth_file_updated: Union[int, None] = None,
) -> Union[Parser, None]:
    """
    Parses a single file and returns the results as a Parser object. This function does
    not access the database.

    Parameters
    ----------
    path_to_file : Path
        path to the file to be parsed

    Returns
    -------
    Union[Parser, None]
        Parser object containing the payload data of the parsed file or None in case parsing fails.
    """
    try:
        parsed_data = _parse_data(str(path_to_file), md5sum)
        if inform_about_nth_file_updated:
            sse.send(f"<b>Progress Update:</b> Parsed {inform_about_nth_file_updated} file(s).", "blue", "DEBUG")
        return parsed_data
    except (FitHeaderError, FitEOFError, AttributeError):
        # FitHeaderError and FitEOFError is used to catch corrupted fit files (e.g. non-fit files having a .fit ending).
        # AttributeError is raised in case of e.g. wahoo files, which are currently not supported by fitparse,
        # see https://github.com/dtcooper/python-fitparse/issues/121.
        sse.send(
            f"Failed to parse fit file <code>{path_to_file.relative_to(path_to_traces)}</code>. File could either be "
            f"corrupted or does not comply with the fit standard.",
            "red",
            "ERROR",
        )


def _parse_all_files(path_to_traces: Path, md5sums_from_db: List[str], reimporting: bool = False) -> List[Delayed]:
    trace_files = _get_all_files(path_to_traces)
    _send_initial_info(len(trace_files), path_to_traces, reimporting)
    tasks = []
    seen_md5sums = {}
    for i, trace in enumerate(trace_files):
        inform_about_nth_file = None
        if (i + 1) % configuration.number_of_activities_in_bulk_progress_update == 0:
            inform_about_nth_file = configuration.number_of_activities_in_bulk_progress_update
        md5sum = calc_md5(trace)
        if md5sum not in seen_md5sums.keys():  # file was not seen yet
            if reimporting:  # add to tasks in case of reimport anyway
                tasks.append(dask.delayed(_parse_single_file)(trace, md5sum, path_to_traces, inform_about_nth_file))
            else:
                if md5sum not in md5sums_from_db:  # not reimporting and not in db -> add to tasks
                    tasks.append(dask.delayed(_parse_single_file)(trace, md5sum, path_to_traces, inform_about_nth_file))
            seen_md5sums[md5sum] = trace
        else:
            msg = (
                f"The following two files have the same checksum, you might want to remove one of them:<ul>"
                f"<li><code>{Path(trace).relative_to(path_to_traces)}</code> and</li>"
                f"<li><code>{Path(seen_md5sums[md5sum]).relative_to(path_to_traces)}</code></li></ul>"
            )
            sse.send(msg, "yellow", "WARNING")
    return tasks


def _save_single_parsed_file_to_db(
    parsed_file: Parser, models: ModuleType, importing_demo_data: bool, update_existing: bool
) -> None:
    # save trace data to model
    trace_file_object = _save_trace_to_model(
        traces_model=models.Traces,
        md5sum=parsed_file.md5sum,
        parser=parsed_file,
        trace_file=parsed_file.path_to_file,
        update_existing=update_existing,
    )
    trace_file_instance = models.Traces.objects.get(pk=trace_file_object.pk)

    # save laps to model
    _save_laps_to_model(
        lap_model=models.Lap, laps=parsed_file.laps, trace_instance=trace_file_instance, update_existing=update_existing
    )
    # save activity itself to model
    activity_object = _save_activity_to_model(
        models=models,
        parser=parsed_file,
        trace_instance=trace_file_instance,
        importing_demo_data=importing_demo_data,
        update_existing=update_existing,
    )
    activity_instance = models.Activity.objects.get(pk=activity_object.pk)
    # save best sections to model
    _save_best_sections_to_model(
        best_section_model=models.BestSection,
        parser=parsed_file,
        activity_instance=activity_instance,
        update_existing=update_existing,
    )
    return activity_instance


def run_importer__dask(models: ModuleType, importing_demo_data: bool = False, reimporting: bool = False) -> None:
    path_to_traces = models.get_settings().path_to_trace_dir
    log.debug(f"triggered file importer on path: {path_to_traces}")

    # get a list of delayed tasks, each for parsing a given activity file
    delayed_tasks = _parse_all_files(path_to_traces, _get_md5sums_from_model(models.Traces), reimporting)

    # compute all tasks in parallel
    all_parsed_files = dask.compute(delayed_tasks)[0]

    # remove Nones from list
    all_parsed_files = [f for f in all_parsed_files if f]

    # save activity data to db sequentially in order to avoid "database is locked" issues
    if all_parsed_files:
        sse.send(f"<b>Progress Update:</b> Saving data of {len(all_parsed_files)} file(s) to db.", "blue", "DEBUG")
        for i, parsed_file in enumerate(all_parsed_files):
            if (i + 1) % configuration.number_of_activities_in_bulk_progress_update == 0:
                sse.send(f"<b>Progress Update:</b> Saved data of {i + 1} files to db.", "blue", "DEBUG")
            _save_single_parsed_file_to_db(
                parsed_file, models, importing_demo_data=importing_demo_data, update_existing=reimporting
            )
    if importing_demo_data:
        demo_activities = models.Activity.objects.filter(is_demo_activity=True)
        change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)
        insert_custom_demo_activities(count=9, every_nth_day=3, activity_model=models.Activity, sport_model=models.Sport)
        log.info("finished inserting demo data")
    _send_result_info(len(all_parsed_files), reimporting)
    log.debug("finished file import")


def _send_result_info(number_of_updated: int, reimporting: bool):
    if reimporting:
        msg = f"<b>Finished Reimport:</b> Updated data of {number_of_updated} file(s)."
    else:
        msg = f"<b>Finished File Import:</b> Imported {number_of_updated} new file(s)."
    sse.send(msg, "green", "INFO")
