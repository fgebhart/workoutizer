import logging
import subprocess
import time
from typing import Tuple

import pyudev

from wkz import models
from wkz.io.fit_collector import collect_fit_files_from_device

RETRIES = 5
WAIT = 20
DEVICE_READY_STRING = "Garmin International"
DEVICE_NOT_READY_STRING = "(various models)"


log = logging.getLogger(__name__)


class FailedToMountDevice(Exception):
    pass


def mount_device_and_collect_files() -> None:
    try:
        path_to_garmin_device = wait_for_device_and_mount()

        # sleep for a second after mounting to avoid IO error
        time.sleep(1)

        settings = models.get_settings()
        collect_fit_files_from_device(
            path_to_garmin_device=path_to_garmin_device,
            target_location=settings.path_to_trace_dir,
            delete_files_after_import=settings.delete_files_after_import,
        )
    except FailedToMountDevice as e:
        log.error(f"Failed to mount device: {e}")


def wait_for_device_and_mount() -> str:
    """
    Function to be called whenever a garmin device is connected via USB. Since it takes a moment for the device to be
    accessible and ready to be mounted we need to wait until the `lsusb` command has "Garmin International" in its
    output.
    """
    if not garmin_device_connected():
        raise FailedToMountDevice("Expected output of 'lsusb' to contain string 'Garmin'.")
    log.debug("checking device to be ready for mount...")
    for _ in range(RETRIES):
        lsusb = _get_lsusb_output()
        if DEVICE_READY_STRING in lsusb and DEVICE_NOT_READY_STRING not in lsusb:
            path = _get_path_to_device(lsusb)
            log.debug("device seems to be ready for mount, mounting...")
            mount_output = _determine_type_and_mount(path)
            if "Mounted" in mount_output:
                mounted_path = _get_mounted_path(mount_output)
                log.info(f"successfully mounted device at: {mounted_path}")
                return mounted_path
            else:
                raise FailedToMountDevice(f"Mount command did not return expected output: {mount_output}")
        else:
            log.info(f"device is not ready for mounting yet, waiting {WAIT} seconds...")
            time.sleep(WAIT)
    log.warning(f"could not mount device within time window of {RETRIES * WAIT} seconds.")
    raise FailedToMountDevice(f"Unable to mount device after {RETRIES} retries, with {WAIT}s delay each.")


def _get_mounted_path(mount_output: str) -> str:
    if "Mounted" not in mount_output:
        raise FailedToMountDevice(
            f"Output of mount command does not look as expected: {mount_output}. Expected to contain 'Mounted'."
        )
    path_start = mount_output.find("at")
    mount_path = mount_output[path_start + 3 :]
    return mount_path


def _get_path_to_device(lsusb_output: str) -> str:
    assert DEVICE_READY_STRING in str(lsusb_output)
    list_of_lines = str(lsusb_output).split("\n")
    path = None
    for line in list_of_lines:
        if DEVICE_READY_STRING in line:
            bus_start = line.find("Bus") + 4
            bus = line[bus_start : bus_start + 3]
            device_start = line.find("Device") + 7
            dev = line[device_start : device_start + 3]
            path = f"/dev/bus/usb/{bus}/{dev}"
            return path


def _mount_device_using_gio(path: str) -> str:
    return subprocess.check_output(["gio", "mount", "-d", path]).decode("utf-8").rstrip()


def _mount_device_using_pmount(path: str) -> str:
    subprocess.check_output(["pmount", path, "garmin"]).decode("utf-8")
    # pmount does not return anything, assume command to be successful and return expected string
    return "Mounted at /media/garmin"


def garmin_device_connected() -> bool:
    try:
        lsusb = _get_lsusb_output()
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise FailedToMountDevice("No 'lsusb' command available on your system.")
    if "Garmin" in lsusb:
        return True
    else:
        return False


def _get_lsusb_output() -> str:
    return subprocess.check_output("lsusb").decode("utf8")


def _determine_type_and_mount(path: str) -> str:
    device_type, path = _determine_device_type(path)
    log.debug(f"device at path {path} is of type {device_type}")
    try:
        if device_type == "MTP":
            return _mount_device_using_gio(path)
        elif device_type == "BLOCK":
            return _mount_device_using_pmount(path)
    except subprocess.CalledProcessError as e:
        raise FailedToMountDevice(f"Execution of mount command failed: {e}")


def _determine_device_type(path: str) -> Tuple[str, str]:
    log.debug(f"trying to determine device type for device at: {path}...")
    try:
        device_tree = pyudev.Context()
    except ImportError:
        raise FailedToMountDevice("Your system seems to lack the udev utility.")

    # check if device is of type MTP
    if _is_of_type_mtp(device_tree):
        return "MTP", path

    # check if device is of type BLOCK
    block_device_path = _get_block_device_path(device_tree, path)
    if block_device_path:
        return "BLOCK", block_device_path
    else:
        raise FailedToMountDevice("Could not determine device type. Device is neither MTP nor BLOCK.")


def _is_of_type_mtp(device_tree: pyudev.core.Context) -> bool:
    devices = device_tree.list_devices(subsystem="usb").match_property("ID_MTP_DEVICE", "1")
    if len(list(devices)) > 0:
        return True
    else:
        return False


def _get_block_device_path(device_tree: pyudev.core.Context, path: str) -> str:
    usb_devices = device_tree.list_devices(subsystem="usb").match_property("DEVNAME", path)
    for device in usb_devices:
        (model_id, vendor_id) = device.get("ID_MODEL_ID"), device.get("ID_VENDOR_ID")
        block_devices = device_tree.list_devices(subsystem="block").match_property("ID_MODEL_ID", model_id)
        for device in block_devices:
            if vendor_id == device.get("ID_VENDOR_ID"):
                return device.get("DEVNAME")
