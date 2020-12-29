import logging
import os
import time
import shutil
import subprocess
from typing import Union

from wizer.tools.utils import files_are_same


log = logging.getLogger("wizer.fit_collector")


class FitCollector:
    def __init__(self, path_to_garmin_device: str, target_location: str, delete_files_after_import: bool = False):
        self.path_to_garmin_device = path_to_garmin_device
        self.delete_files_after_import = delete_files_after_import
        self.activity_path = "/Primary/GARMIN/Activity/"
        self.target_location = os.path.join(target_location, "garmin")
        if not os.path.isdir(self.target_location):
            os.makedirs(self.target_location)

    def copy_fit_files(self):
        log.debug(f"looking for garmin device at: {self.path_to_garmin_device}")
        garmin_watch = _find_complete_garmin_device_path(self.path_to_garmin_device)
        if garmin_watch:
            garmin_watch = garmin_watch + self.activity_path
            if os.path.isdir(garmin_watch):
                fits = [
                    os.path.join(root, name)
                    for root, dirs, files in os.walk(garmin_watch)
                    for name in files
                    if name.endswith(".fit")
                ]
                for fit in fits:
                    file_name = str(fit.split("/")[-1])
                    target_file = os.path.join(self.target_location, file_name)
                    if not os.path.isfile(target_file):
                        shutil.copy(fit, target_file)
                        log.debug(f"copied file: {file_name}")
                        if files_are_same(fit, target_file):
                            log.debug(f"files {fit} and {target_file} are equal")
                            if self.delete_files_after_import:
                                log.debug(f"deleting fit file from device: {fit}")
                                os.remove(fit)
                        else:
                            log.warning(f"files {fit} and {target_file} are NOT equal after copying.")


def _find_complete_garmin_device_path(begin_of_path_to_device: str) -> Union[str, None]:
    complete_paths = [
        os.path.join(root, name)
        for root, dirs, files in os.walk(begin_of_path_to_device)
        for name in dirs
        if name.startswith("mtp:host")
    ]
    if complete_paths:
        return complete_paths[0]
    else:
        return None


def try_to_mount_device():
    log.debug("trying to mount device...")
    time.sleep(3)
    lsusb_output = subprocess.check_output("lsusb")
    split = str(lsusb_output).split("`\\n")
    mount_output = None
    for line in split:
        if "Garmin" in line:
            log.debug(f"found Garmin device in: {line}")
            bus_start = line.find("Bus") + 4
            bus = line[bus_start : bus_start + 3]
            device_start = line.find("Device") + 7
            dev = line[device_start : device_start + 3]
            try:
                mount_output = _mount_device_using_gio(bus, dev)
            except subprocess.CalledProcessError as e:
                log.warning(f"could not mount device: {e}")
                return None
        else:
            log.debug(f"no Garmin device found in 'lsusb' line: {line}")
    if mount_output:
        if "Mounted" in mount_output:
            path_start = mount_output.find("at")
            mount_path = mount_output[path_start + 2 : -1]
            log.info(f"successfully mounted device at: {mount_path}")
            return mount_path
        else:
            log.warning("could not mount device")
    else:
        log.warning("Found Garmin device, but could not mount it.")


def _mount_device_using_gio(bus: str, dev: str) -> str:
    return subprocess.check_output(["gio", "mount", "-d", f"/dev/bus/usb/{bus}/{dev}"]).decode("utf-8")


def unmount_device_using_gio(path_to_device):
    complete_device_path = _find_complete_garmin_device_path(path_to_device)
    log.debug(f"unmounting device at: {complete_device_path}")
    time.sleep(1)
    return subprocess.check_output(["gio", "mount", "-u", complete_device_path])
