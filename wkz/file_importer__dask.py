from typing import List
import logging
from pathlib import Path
from types import ModuleType

import dask
from dask.delayed import Delayed
from django.db.utils import IntegrityError
from fitparse.utils import FitHeaderError, FitEOFError

from wkz.file_importer import (
    _parse_data,
    _get_all_files,
    _get_md5sums_from_model,
    _save_trace_to_model,
    _save_laps_to_model,
    _save_activity_to_model,
    _save_best_sections_to_model,
    change_date_of_demo_activities,
    insert_custom_demo_activities,
    ImportProgressMetaData,
)
from wkz.tools.utils import calc_md5
from wkz.tools import sse
from wkz.file_helper.parser import Parser


log = logging.getLogger(__name__)


def _parse_single_file(
    path_to_file: Path,
    md5sum: str,
) -> Parser:
    """
    Parses a single file and returns the results as a Parser object. This function does
    not access the database.

    Parameters
    ----------
    path_to_file : Path
        path to the file to be parsed

    Returns
    -------
    Parser
        Parser object containing the payload data of the parsed file
    """
    try:
        parsed_data = _parse_data(str(path_to_file), md5sum)
        return parsed_data
    except (FitHeaderError, FitEOFError):
        sse.send(
            f"Failed to parse fit file: '{path_to_file}'. File could either be "
            f"corrupted or does not comply with the fit standard.",
            "red",
            "ERROR",
        )


def _parse_all_files(path_to_traces: Path, md5sums_from_db: List[str], reimporting: bool = False) -> List[Delayed]:
    trace_files = _get_all_files(path_to_traces)
    if not trace_files:
        sse.send(f"No activity files found in '{path_to_traces}'.", "yellow", "WARNING")
    tasks = []
    for trace in trace_files:
        md5sum = calc_md5(trace)
        if md5sum in md5sums_from_db:
            if not reimporting:
                sse.send(f"File '{trace.relative_to(path_to_traces)}' is in db already.", "yellow", "WARNING")
            else:
                tasks.append(dask.delayed(_parse_single_file)(trace, md5sum))
        else:
            tasks.append(dask.delayed(_parse_single_file)(trace, md5sum))
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

    md = ImportProgressMetaData()
    md.files_found_cnt = len(all_parsed_files)
    # save activity data to db sequentially
    for parsed_file in all_parsed_files:
        if parsed_file:
            try:
                _save_single_parsed_file_to_db(
                    parsed_file, models, importing_demo_data=importing_demo_data, update_existing=reimporting
                )
            except IntegrityError:
                trace = models.Traces.objects.get(md5sum=parsed_file.md5sum)
                sse.send(
                    f"The following two files have the same checksum, "
                    f"you might want to remove one of them:\n<ul>"
                    f"<li>{parsed_file.path_to_file}</li>"
                    f"<li>{trace.path_to_file}</li></ul>",
                    "yellow",
                    "WARNING",
                )
    if importing_demo_data:
        demo_activities = models.Activity.objects.filter(is_demo_activity=True)
        change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)
        insert_custom_demo_activities(count=9, every_nth_day=3, activity_model=models.Activity, sport_model=models.Sport)
        log.info("finished inserting demo data")
    log.debug("finished file import")
