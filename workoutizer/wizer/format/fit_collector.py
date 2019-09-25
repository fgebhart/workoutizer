import logging
import os
import shutil

log = logging.getLogger("wizer.fit_collector")


class FitCollector:
    def __init__(self, settings_model):
        self.settings = settings_model
        self.activity_path = "/Primary/GARMIN/Activity/"

    def look_for_fit_files(self):
        settings = self.settings.objects.get(pk=1)
        path_to_gvfs = settings.path_to_garmin_device
        log.debug(f"looking for garmin device at: {path_to_gvfs}")
        settings = self.settings.objects.all().order_by('-id').first()
        target_location = os.path.join(settings.path_to_trace_dir, 'garmin')
        garmin_watch = [os.path.join(root, name) for root, dirs, files in os.walk(path_to_gvfs)
                        for name in dirs if name.startswith("mtp:host")]
        if garmin_watch:
            garmin_watch = garmin_watch[0] + self.activity_path
            if os.path.isdir(garmin_watch):
                fits = [os.path.join(root, name) for root, dirs, files in os.walk(garmin_watch)
                        for name in files if name.endswith(".fit")]
                for fit in fits:
                    file_name = str(fit.split("/")[-1])
                    target_file = os.path.join(target_location, file_name)
                    if not os.path.isfile(target_file):
                        shutil.copy(fit, target_file)
                        log.debug(f"copied file: {file_name}")
