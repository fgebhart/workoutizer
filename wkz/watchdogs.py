import logging
import os
from pathlib import Path

from wkz import models
from wkz.file_helper.fit_collector import FitCollector
from wkz.file_importer import run_importer__dask

log = logging.getLogger(__name__)


def trigger_file_watchdog():
    settings = models.get_settings()
    if Path(settings.path_to_trace_dir).is_dir():
        run_importer__dask(models)
    else:
        log.warning(f"File Watchdog: {settings.path_to_trace_dir} is not a valid directory.")


def trigger_device_watchdog():
    settings = models.get_settings()
    log.debug(f"checking for mounted device at '{settings.path_to_garmin_device}' ...")

    _watch_for_device(
        path_to_trace_dir=settings.path_to_trace_dir,
        path_to_garmin_device=settings.path_to_garmin_device,
        delete_files_after_import=settings.delete_files_after_import,
    )


def _watch_for_device(path_to_garmin_device: str, path_to_trace_dir: str, delete_files_after_import: bool):
    if Path(path_to_garmin_device).is_dir():
        sub_dirs = []
        for filename in os.listdir(path_to_garmin_device):
            if (Path(path_to_garmin_device) / filename).is_dir():
                sub_dirs.append(sub_dirs)
        if len(sub_dirs) > 0:
            log.info(f"Found mounted device at {path_to_garmin_device}, triggering fit collector...")
            fit_collector = FitCollector(
                path_to_garmin_device=path_to_garmin_device,
                target_location=path_to_trace_dir,
                delete_files_after_import=delete_files_after_import,
            )
            fit_collector.copy_fit_files()
    else:
        log.warning(f"Device Watchdog: {path_to_garmin_device} is not a valid directory.")
