import logging
import os
import shutil
import subprocess

log = logging.getLogger("wizer.fit_collector")


class FitCollector:
    def __init__(self, path_to_garmin_device: str, target_location: str, delete_files_after_import: bool = False):
        self.path_to_garmin_device = path_to_garmin_device
        self.delete_files_after_import = delete_files_after_import
        self.activity_path = "/Primary/GARMIN/Activity/"
        self.target_location = os.path.join(target_location, 'garmin')
        if not os.path.isdir(self.target_location):
            os.makedirs(self.target_location)

    def copy_fit_files(self):
        log.debug(f"looking for garmin device at: {self.path_to_garmin_device}")
        garmin_watch = [os.path.join(root, name) for root, dirs, files in os.walk(self.path_to_garmin_device)
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
                        if self.delete_files_after_import:
                            _delete_imported_fit_file_from_device(
                                path_to_file_on_device=fit,
                                path_to_local_file=target_file,
                            )


def _delete_imported_fit_file_from_device(path_to_file_on_device: str, path_to_local_file: str):
    """
    Check if both the original file on the device and the copy on the local file
    system are present and if so, delete the file on the device.
    """
    if os.path.isfile(path_to_file_on_device) and os.path.isfile(path_to_local_file):
        os.remove(path_to_file_on_device)
        log.debug(f"deleted file from device: {path_to_file_on_device}")


def try_to_mount_device():
    lsusb_output = subprocess.check_output("lsusb")
    split = str(lsusb_output).split("\\n")
    mount_output = None
    for line in split:
        if "Garmin" in line:
            bus_start = line.find("Bus") + 4
            bus = line[bus_start:bus_start + 3]
            device_start = line.find("Device") + 7
            dev = line[device_start:device_start + 3]
            try:
                mount_output = subprocess.check_output(["gio", "mount", "-d", f"/dev/bus/usb/{bus}/{dev}"]).decode(
                    'utf-8')
            except subprocess.CalledProcessError as e:
                log.warning(f"could not mount device: {e}")
                return None
    if mount_output:
        if "Mounted" in mount_output:
            path_start = mount_output.find("at")
            mount_path = mount_output[path_start + 2:-1]
            log.info(f"successfully mounted device at: {mount_path}")
            return mount_path
        else:
            log.warning(f"could not mount device")
    else:
        log.warning(f"no Garmin device found in 'lsusb'")
