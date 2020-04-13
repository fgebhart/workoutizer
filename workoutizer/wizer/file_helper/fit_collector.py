import logging
import os
import shutil

log = logging.getLogger("wizer.fit_collector")


class FitCollector:
    def __init__(self, settings_model):
        self.settings = settings_model
        self.activity_path = "/Primary/GARMIN/Activity/"
        self.settings = self.settings.objects.get(pk=1)
        self.path_to_gvfs = self.settings.path_to_garmin_device
        self.target_location = os.path.join(self.settings.path_to_trace_dir, 'garmin')
        log.debug(f"looking for garmin device at: {self.path_to_gvfs}")

    def look_for_fit_files_and_copy(self):
        self.path_to_gvfs = self.settings.path_to_garmin_device
        self.target_location = os.path.join(self.settings.path_to_trace_dir, 'garmin')

        garmin_watch = [os.path.join(root, name) for root, dirs, files in os.walk(self.path_to_gvfs)
                        for name in dirs if name.startswith("mtp:host")]
        if garmin_watch:
            garmin_watch = garmin_watch[0] + self.activity_path
            if os.path.isdir(garmin_watch):
                fits = [os.path.join(root, name) for root, dirs, files in os.walk(garmin_watch)
                        for name in files if name.endswith(".fit")]
                for fit in fits:
                    file_name = str(fit.split("/")[-1])
                    target_file = os.path.join(self.target_location, file_name)
                    if not os.path.isfile(target_file):
                        shutil.copy(fit, target_file)
                        log.debug(f"copied file: {file_name}")
                        if self.settings.delete_files_after_import:
                            delete_imported_fit_file_from_device(
                                path_to_file_on_device=fit,
                                path_to_local_file=target_file,
                            )


def delete_imported_fit_file_from_device(path_to_file_on_device: str, path_to_local_file: str):
    """
    Check if both the original file on the device and the copy on the local file
    system are present and if so, delete the file on the device.
    """
    if os.path.isfile(path_to_file_on_device) and os.path.isfile(path_to_local_file):
        os.remove(path_to_file_on_device)
        log.debug(f"deleted file from device: {path_to_file_on_device}")
