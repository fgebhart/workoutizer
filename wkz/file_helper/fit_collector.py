import logging
import os
import shutil
import subprocess
from typing import List, Tuple, Union

import pyudev

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
            fits = [
                os.path.join(root, name)
                for root, dirs, files in os.walk(activity_path)
                for name in files
                # Some devices genereate file named .FIT, other .fit
                if name.lower().endswith(".fit")
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
                        if self.delete_files_after_import:
                            os.remove(fit)
                            log.debug(f"deleted fit file from device: {file_name}")
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
            (type, path) = _find_device_type(bus, dev)
            log.debug(f"device type is {type} with {path}")
            if type == "MTP":
                mount_output = _mount_device_using_gio(path)
            elif type == "BLOCK":
                mount_output = _mount_device_using_pmount(path)
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
        log.warning(f"Found Garmin device, but could not mount it. {mount_output}")


def _mount_device_using_gio(path: str) -> str:
    return subprocess.check_output(["gio", "mount", "-d", path]).decode("utf-8")


def _mount_device_using_pmount(path: str) -> str:
    subprocess.check_output(["pmount", path, "garmin"]).decode("utf-8")
    return "Mounted at /media/garmin"


def _find_device_type(bus: str, dev: str) -> Tuple[str, str]:
    log.debug("Looking up type of device")
    device_tree = pyudev.Context()
    usb_devices = device_tree.list_devices(subsystem="usb").match_property("DEVNAME", f"/dev/bus/usb/{bus}/{dev}")
    for device in usb_devices:
        if str(device.get("ID_MTP_DEVICE")) == str(1):
            log.debug("Device is an MTP device")
            return ("MTP", f"/dev/bus/usb/{bus}/{dev}")
        else:
            log.debug("Device is block device")
            (model_id, vendor_id) = device.get("ID_MODEL_ID"), device.get("ID_VENDOR_ID")
            block_devices = device_tree.list_devices(subsystem="block").match_property("ID_MODEL_ID", model_id)
            for device in block_devices:
                if vendor_id == device.get("DEVNAME"):
                    return ("BLOCK", device.get("DEVNAME"))
