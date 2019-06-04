import logging

from django.apps import AppConfig


log = logging.getLogger('wizer')


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        log.debug("apps successfully loaded")


class FileChecker:

    def __init__(self):
        from .models import Settings
        settings = Settings.objects.get(id=1)
        print(f"path to trace dir: {settings.path_to_trace_dir}")
