from typing import List, Union
import logging
from pathlib import Path
from types import ModuleType

import dask
from dask.delayed import Delayed
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
    _send_initial_info,
)
from wkz.tools.utils import calc_md5
from wkz import configuration
from wkz.tools import sse
from wkz.file_helper.parser import Parser


log = logging.getLogger(__name__)


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
