import time
import os
import logging
import hashlib
from multiprocessing import Process

from django.apps import AppConfig

log = logging.getLogger('wizer.filechecker')


class WizerConfig(AppConfig):
    name = 'wizer'
    verbose_name = 'wizer django app'

    def ready(self):
        from .models import Settings
        from .models import TraceFiles
        settings = Settings.objects.all().order_by('-id').first()
        p = Process(target=FileChecker, args=(settings.path_to_trace_dir, TraceFiles))
        p.start()


class FileChecker:
    def __init__(self, path, trace_files_model):
        self.path = path
        self.trace_files_model = trace_files_model
        self.start_listening()

    def start_listening(self):
        while True:
            # find trace files in dir
            trace_files = [os.path.join(root, name)
                           for root, dirs, files in os.walk(self.path)
                           for name in files if name.endswith(".gpx")]
            log.debug(f"file checker found files in trace dir: {trace_files}")
            self.save_files_to_db(trace_files)

            time.sleep(100)

    def save_files_to_db(self, trace_files):
        md5sums_from_db = list(self.trace_files_model.objects.all())
        md5sums_from_db = [m.md5sum for m in md5sums_from_db]
        for file in trace_files:
            md5sum = calc_md5(file)
            if md5sum not in md5sums_from_db:
                log.info(f"adding file {file} with md5sum {md5sum} to db")
                t = self.trace_files_model(path_to_file=file, md5sum=md5sum)
                t.save()


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
