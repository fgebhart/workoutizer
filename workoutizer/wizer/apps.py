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
        settings = Settings.objects.get(id=1)
        p = Process(target=FileChecker, args=(settings.path_to_trace_dir,))
        p.start()
        log.warning("sent to background - starting django")


class FileChecker:
    def __init__(self, path):
        self.path = path
        log.debug(f"going to listen for new files in dir: {path}")
        self.start_listening()

    def start_listening(self):
        while True:
            files_in_dir = os.listdir(path=self.path)
            log.debug(f"found files: {files_in_dir}")
            time.sleep(3)


