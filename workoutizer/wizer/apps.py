import time
import os
import logging
from multiprocessing import Process

from django.apps import AppConfig

log = logging.getLogger('wizer')


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        log.debug("apps successfully loaded")
        from .models import Settings
        settings = Settings.objects.all().order_by('-id').first()
        print(settings.path_to_trace_dir)
        p = Process(target=FileChecker, args=(settings.path_to_trace_dir,))
        p.start()
        log.debug("sent file checker to background - starting django...")


class FileChecker:
    def __init__(self, path):
        self.path = path
        log.debug(f"going to listen for new files in dir: {path}")
        self.start_listening()

    def start_listening(self):
        while True:
            gpx_files = [os.path.join(root, name)
                         for root, dirs, files in os.walk(self.path)
                         for name in files if name.endswith(".gpx")]

            files_in_dir = os.listdir(path=self.path)
            log.debug(f"found files: {gpx_files}")
            time.sleep(10)
