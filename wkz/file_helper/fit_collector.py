import logging
import os
import time
import shutil
import subprocess
from typing import Union, List

from wkz.tools.utils import files_are_same


log = logging.getLogger(__name__)


class FitCollector:
    def __init__(
        self,
        path_to_garmin_device: str,
        target_location: str,
        delete_files_after_import: bool = False,
    ):
        self.path_to_garmin_device = path_to_garmin_device
        self.delete_files_after_import = delete_files_after_import
        self.activity_dir_name = "Activity"
        self.sub_dir_for_garmin_files = "garmin"
        self.target_location = os.path.join(target_location, self.sub_dir_for_garmin_files)
        if not os.path.isdir(self.target_location):
            os.makedirs(self.target_location)

    def copy_fit_files(self):
        log.debug("looking for new activity files in garmin device")
        activity_path = _find_activity_sub_dir_in_path(
            name_of_dir=self.activity_dir_name,
            path=self.path_to_garmin_device,
            depth=4,
        )
        if activity_path:
            log.debug(f"found activity dir at: {activity_path}")
            time.sleep(3)
            fits = [
                os.path.join(root, name)
                for root, dirs, files in os.walk(activity_path)
                for name in files
                if name.endswith(".fit")
            ]
            if fits:
                no_file_was_copied = True
                for fit in fits:
                    file_name = str(fit.split("/")[-1])
                    target_file = os.path.join(self.target_location, file_name)
                    if not os.path.isfile(target_file):
                        shutil.copy(fit, target_file)
                        log.info(f"copied file: {target_file}")
                        no_file_was_copied = False
                        if files_are_same(fit, target_file):
                            log.debug(f"files {fit} and {target_file} are equal")
                            if self.delete_files_after_import:
                                log.debug(f"deleting fit file from device: {file_name}")
                                os.remove(fit)
                        else:
                            log.warning(f"files {fit} and {target_file} are NOT equal after copying.")
                if no_file_was_copied:
                    log.info("No new file found.")
            else:
                log.debug(f"Could not find any activity fit files at {activity_path}")
        else:
            log.warning(f"No directory named {self.activity_dir_name} found in path {self.path_to_garmin_device}")


def _find_activity_sub_dir_in_path(name_of_dir: str, path: str, depth: int = 3) -> Union[str, bool]:
    def _get_all_subfolders(paths: List[str]) -> List[str]:
        sub_dirs = []
        for path in paths:
            sub_dirs += [f for f in os.scandir(path) if f.is_dir()]
        return sub_dirs

    paths = [path]
    for _ in range(depth):
        sub_dirs = _get_all_subfolders(paths)
        for sub_dir in sub_dirs:
            if name_of_dir.lower() == sub_dir.name.lower():
                return sub_dir.path
        paths = sub_dirs
    # if this line is reach it means the dir was not found
    return False


def try_to_mount_device():
    log.debug("trying to mount device...")
    time.sleep(3)
    lsusb_output = subprocess.check_output("lsusb")
    split = str(lsusb_output).split("\\n")
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
                log.warning(f"could not mount device: {e}", exc_info=True)
                return None
        else:
            # log.debug(f"no Garmin device found in 'lsusb' line: {line}")
            pass
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
