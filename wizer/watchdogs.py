import os
import sys
import logging
from types import ModuleType
from pathlib import Path
import threading
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.apps import AppConfig

from wizer import configuration
from wizer.file_importer import import_activity_files
from wizer.file_helper.fit_collector import FitCollector
from workoutizer import settings as django_settings


log = logging.getLogger(__name__)


class ActivityFilesWatchdog(AppConfig):
    """
    The below ready function is the entry point for django to trigger when apps are loaded.
    This class is registered in wizer.__init__.py and will start watchdogs for file
    monitoring.
    """

    name = "wizer"

    def ready(self):
        # ensure to only run with 'manage.py runserver' and not in auto reload thread
        if _was_runserver_triggered(sys.argv) and os.environ.get("RUN_MAIN", None) != "true":
            log.info(f"using workoutizer home at {django_settings.WORKOUTIZER_DIR}")
            from wizer import models

            # initially run importing once to ensure all files are imported
            import_activity_files(models, importing_demo_data=False)

            # start watchdog to monitor whether a new device was mounted
            settings = models.get_settings()
            path_to_garmin_device = settings.path_to_garmin_device
            _start_device_watchdog(path_to_garmin_device, settings.path_to_trace_dir, settings.delete_files_after_import)

            # start watchdog for new files being placed into the tracks directory
            _start_file_importer_watchdog(path=django_settings.TRACKS_DIR, models=models)


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


class FileImporterHandler(FileSystemEventHandler):
    """Watchdog to trigger the import of newly added activity files"""

    def __init__(self, models):
        self.models = models
        super().__init__()

    def on_created(self, event):
        if event.src_path.split(".")[-1] in configuration.supported_formats:
            log.debug("activity file was added, triggering file importer...")

            import_activity_files(self.models, importing_demo_data=False)


def _start_file_importer_watchdog(path: str, models: ModuleType):
    """
    Watchdog to monitor the trace dir for new incoming activity files. Starts the
    FileImporterHandler which triggers the import of a newly added .fit or .gpx file.

    Parameters
    ----------
    path : str
        path to the trace dir, which should be watched
    models : ModuleType
        the workoutizer models
    """
    if Path(path).is_dir():
        event_handler = FileImporterHandler(models)
        watchdog = Observer()
        watchdog.schedule(event_handler, path=path, recursive=True)
        watchdog.start()
        log.debug(f"started watchdog for incoming activity files in {path}")
    else:
        log.warning(f"Path to trace dir {path} does not exist. File Importer watchdog is disabled.")


def _watch_for_device(path_to_garmin_device: str, path_to_trace_dir: str, delete_files_after_import: bool):
    device_mounted = False
    while True:
        sub_dirs = [f for f in os.scandir(path_to_garmin_device) if f.is_dir()]
        if len(sub_dirs) == 1 and not device_mounted:
            device_mounted = True
            log.info(f"New device got mounted at {path_to_garmin_device}, triggering fit collector...")
            fit_collector = FitCollector(
                path_to_garmin_device=path_to_garmin_device,
                target_location=path_to_trace_dir,
                delete_files_after_import=delete_files_after_import,
            )
            fit_collector.copy_fit_files()
        elif len(sub_dirs) == 0:
            device_mounted = False
        time.sleep(1)


def _start_device_watchdog(path_to_garmin_device: str, path_to_trace_dir: str, delete_files_after_import: bool):
    """
    Watchdog to watch for garmin devices being mounted. The activity directory is
    determined and all new fit files are copied to the wkz trace dir.

    Parameters
    ----------
    path_to_garmin_device : str
        path to dir in which garmin device gets mounted in
    path_to_trace_dir : str
        path to trace dir, to which new activity files should copied to
    delete_files_after_import: bool
        whether copied activity files should be deleted from garmin device
    """

    if Path(path_to_garmin_device).is_dir():
        t = threading.Thread(
            target=_watch_for_device,
            args=(
                path_to_garmin_device,
                path_to_trace_dir,
                delete_files_after_import,
            ),
            daemon=True,
        )
        t.start()
        log.debug(f"started watchdog for device being mounted at {path_to_garmin_device}")
    else:
        log.warning(f"Device mount path {path_to_garmin_device} does not exist. Device watchdog is disabled.")
