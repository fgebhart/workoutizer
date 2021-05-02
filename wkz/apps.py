import os
import sys
import logging
from types import ModuleType
from pathlib import Path
import threading
import time

from django_eventstream import send_event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.apps import AppConfig

from wkz import configuration
from wkz.tools.utils import Singleton
from wkz.file_importer import import_activity_files
from wkz.file_helper.fit_collector import FitCollector
from workoutizer import settings as django_settings


log = logging.getLogger(__name__)


class ActivityFilesAndDeviceWatchdog(AppConfig):
    """
    The below ready function is the entry point for django to trigger when apps are loaded.
    This class is registered in wkz.__init__.py and will start watchdogs for file
    monitoring.
    """

    name = "wkz"

    def ready(self):
        # ensure to only run with 'manage.py runserver' and not in auto reload thread
        if _was_runserver_triggered(sys.argv) and os.environ.get("RUN_MAIN", None) != "true":
            log.info(f"using workoutizer home at {django_settings.WORKOUTIZER_DIR}")
            from wkz import models

            settings = models.get_settings()

            # start watchdog for new files being placed into the tracks directory
            fw = FileWatchdog(models=models)
            fw.watch()

            # start watchdog to monitor whether a new device was mounted
            path_to_garmin_device = settings.path_to_garmin_device
            _start_device_watchdog(path_to_garmin_device, settings.path_to_trace_dir, settings.delete_files_after_import)


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
        self.locked = False
        super().__init__()

    def on_created(self, event):
        if event.src_path.split(".")[-1] in configuration.supported_formats:
            log.debug("activity file was added, triggering file importer...")
            self.run_activity_import()

    def run_activity_import(self):
        if not self.locked:
            self.locked = True
            import_activity_files(self.models, importing_demo_data=False)
            self.locked = False
        else:
            log.debug("blocked FileImporterHandler from triggering another import process")


class FileWatchdog(metaclass=Singleton):
    """
    Watchdog to monitor the trace dir for new incoming activity files. Starts the
    FileImporterHandler which triggers the import of a newly added .fit or .gpx file.
    The method `watch` can be called repeatedly and will stop watching the previous
    path and start watching the new given path.
    """

    def __init__(self, models: ModuleType):
        self.models = models
        self.watchdog = None

    def watch(self):
        self._reinit_observer()
        settings = self.models.get_settings()
        path = settings.path_to_trace_dir
        if Path(path).is_dir():
            event_handler = FileImporterHandler(self.models)
            event_handler.run_activity_import()
            self.watchdog.schedule(event_handler, path=path, recursive=True)
            self.watchdog.start()
            log.debug(f"started watchdog for incoming activity files in {path}")
            send_event("event", "message", {"text": "watchdog started.", "color": "green"})
        else:
            log.warning(f"Path to trace dir {path} does not exist. File Importer watchdog is disabled.")
            send_event("event", "message", {"text": "invalid path.", "color": "red"})

    def _reinit_observer(self):
        if self.watchdog:
            self.watchdog.unschedule_all()
        self.watchdog = Observer()


def _watch_for_device(path_to_garmin_device: str, path_to_trace_dir: str, delete_files_after_import: bool):
    device_mounted = False
    while True:
        sub_dirs = os.listdir(path_to_garmin_device)
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
