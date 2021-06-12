import os
import logging
import json
from pathlib import Path
from typing import List, Union, Dict, Tuple
from types import ModuleType

from fitparse.utils import FitHeaderError, FitEOFError
from django.db.models import Model
from dask.distributed import Client, as_completed

from wkz.file_helper.parser import Parser
from wkz.file_helper.gpx_parser import GPXParser
from wkz.file_helper.fit_parser import FITParser
from wkz.file_helper.auto_naming import get_automatic_name
from wkz.tools.utils import sanitize, calc_md5, limit_string
from wkz.tools import sse
from wkz.demo import finalize_demo_activity_insertion
from wkz.best_sections.generic import GenericBestSection
from wkz import configuration


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
            # ascent/descent
            total_ascent=parser.total_ascent,
            total_descent=parser.total_descent,
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
    log.info(f"importing {file} ...")
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
    path_to_traces: Path,
    md5sum: str,
) -> Union[Parser, None]:
    """
    Parses a single file and returns the results as a Parser object. This function does
    not access the database.

    Parameters
    ----------
    path_to_file : Path
        path to the file to be parsed
    path_to_traces: Path
        path to the directory containing the activity files
    md5sum: str
        computed md5sum of the file to be parsed

    Returns
    -------
    Union[Parser, None]
        Parser object containing the payload data of the parsed file or None in case parsing fails.
    """
    try:
        parsed_data = _parse_data(str(path_to_file), md5sum)
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


def _save_single_parsed_file_to_db(
    parsed_file: Parser, models: ModuleType, importing_demo_data: bool, update_existing: bool
) -> None:
    log.info(f"saving data of file {parsed_file.file_name} to db...")
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


def _check_and_parse_file(
    path_to_file: Path, path_to_traces: Path, md5sums_from_db: List[str], reimporting: bool
) -> Tuple[str, Path, Union[Parser, None]]:
    if reimporting:
        md5sum = calc_md5(path_to_file)
        return md5sum, path_to_file, _parse_single_file(path_to_file, path_to_traces, md5sum)
    else:
        md5sum = calc_md5(path_to_file)
        if md5sum not in md5sums_from_db:
            return md5sum, path_to_file, _parse_single_file(path_to_file, path_to_traces, md5sum)
        else:
            return md5sum, path_to_file, None


def run_importer__dask(models: ModuleType, importing_demo_data: bool = False, reimporting: bool = False) -> None:
    path_to_traces = models.get_settings().path_to_trace_dir
    log.debug(f"triggered file importer on path: {path_to_traces}")

    trace_files = _get_all_files(path_to_traces)
    _send_initial_info(len(trace_files), path_to_traces)
    md5sums_from_db = _get_md5sums_from_model(models.Traces)

    num = 0
    seen_md5sums = {}
    if trace_files:
        client = Client(processes=False)
        with client:
            distributed_results = client.map(
                _check_and_parse_file,
                trace_files,
                path_to_traces=path_to_traces,
                md5sums_from_db=md5sums_from_db,
                reimporting=reimporting,
            )

            # loop over futures in a sequential fashion to store data to sqlite db sequentially
            for future in as_completed(distributed_results):
                md5sum, path_to_file, parsed_file = future.result()
                # keep track of the seen md5sums and their file path
                seen_md5sums = _keep_track_of_md5sums_and_warn_about_duplicates(seen_md5sums, path_to_file, md5sum)
                # check if result is not None (due to failed parsing)
                if parsed_file:
                    # write parsed file to db if it does not exist yet, or in case of reimporting (=overwriting)
                    if _should_be_written_to_db(parsed_file, models.Traces, reimporting):
                        _save_single_parsed_file_to_db(parsed_file, models, importing_demo_data, reimporting)
                        num += 1
                if (num + 1) % configuration.num_activities_in_progress_update == 0:
                    msg = f"<b>Progress Update:</b> Imported {num + 1} files."
                    sse.send(msg, "blue", "DEBUG")
    _send_result_info(num)

    if importing_demo_data:
        finalize_demo_activity_insertion(models)
    log.debug("finished file import.")


def _keep_track_of_md5sums_and_warn_about_duplicates(
    seen_md5sums: Dict[str, Path], path_to_file: Path, md5sum: str
) -> Dict[str, Path]:
    if md5sum in seen_md5sums.keys():
        msg = (
            f"The following two files have the same checksum, you might want to remove one of them:<ul>"
            f"<li><code>{path_to_file}</code> and </li>"
            f"<li><code>{seen_md5sums[md5sum]}</code></li></ul>"
        )
        sse.send(msg, "yellow", "WARNING")
    else:
        seen_md5sums[md5sum] = path_to_file
    return seen_md5sums


def _should_be_written_to_db(parsed_file: Parser, traces_model: Model, reimporting: bool) -> bool:
    if reimporting:
        return True
    else:
        if traces_model.objects.filter(md5sum=parsed_file.md5sum).exists():
            existing_trace = traces_model.objects.get(md5sum=parsed_file.md5sum)
            msg = (
                f"The following two files have the same checksum, you might want to remove one of them:<ul>"
                f"<li><code>{existing_trace.path_to_file}</code> and </li>"
                f"<li><code>{parsed_file.path_to_file}</code></li></ul>"
            )
            sse.send(msg, "yellow", "WARNING")
            return False
        else:
            return True


def _send_result_info(number_of_updated: int) -> None:
    if number_of_updated == 0:
        msg = "<b>Finished File Import:</b> No new files imported."
    else:
        msg = f"<b>Finished File Import:</b> Imported {number_of_updated} new file(s)."
    sse.send(msg, "green", "DEBUG")


def _send_initial_info(number_of_activities: int, path_to_trace_dir: str):
    sse.send(
        f"<b>File Import started:</b> Found {number_of_activities} activity files in "
        f"<code>{path_to_trace_dir}</code>. Please wait.",
        "blue",
    )
