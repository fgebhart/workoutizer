import os
import sys
import logging
import time
from types import ModuleType

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.apps import AppConfig

from wizer import configuration
from wizer.file_importer import import_activity_files
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

            # initially always trigger importing of files in case new files have been added
            import_activity_files(models, importing_demo_data=False)

            # start watchdog for new files being placed into the tracks directory
            _start_file_importer_watchdog(path=django_settings.TRACKS_DIR, models=models)

            # start watchdog to monitor whether a new device was mounted


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

    def on_any_event(self, event):
        if event.event_type == "created":
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

    event_handler = FileImporterHandler(models)
    watchdog = Observer()
    watchdog.schedule(event_handler, path=path, recursive=True)
    watchdog.start()
    log.debug(f"started watchdog to watch for incoming activity files in {path}")


class DeviceHandler(FileSystemEventHandler):
    """Watchdog to trigger copying activity files from mounted devices"""

    def __init__(self, models):
        self.models = models
        super().__init__()

    def on_created(self, event):
        time.sleep(1)
        log.debug("device mounted at")

        # TODO trigger fit collector here?!


def _start_device_watchdog(path: str, models: ModuleType):
    """
    Watchdog to watch for garmin devices being mounted. The activity directory is
    determined and all new fit files are copied to the wkz trace dir.

    Parameters
    ----------
    path : str
        path to the trace dir, which should be watched
    models : ModuleType
        the workoutizer models
    """

    event_handler = DeviceHandler(models)
    watchdog = Observer()
    watchdog.schedule(event_handler, path=path, recursive=True)
    watchdog.start()
    log.debug(f"started watchdog to watch for device being mounted at {path}")
