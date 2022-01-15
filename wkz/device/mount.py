import logging
import subprocess
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Union

import pyudev

from wkz import models
from wkz.io.fit_collector import collect_fit_files_from_device

RETRIES = 5
WAIT = 20
DEVICE_READY_STRING = "Garmin International"
DEVICE_NOT_READY_STRING = "(various models)"
EXPECTED_MTP_DEVICE_PATH = Path("/run/user/1000/gvfs/")
EXPECTED_BLOCK_DEVICE_PATH = Path("/media/garmin/")


log = logging.getLogger(__name__)


class FailedToMountDevice(Exception):
    pass


class DeviceType(Enum):
    MTP = "mtp"
    BLOCK = "block"


def mount_device_and_collect_files() -> None:
    try:
        path_to_garmin_device = _get_path_of_mounted_device()
        if path_to_garmin_device:
            log.debug(f"found mounted garmin device at: {path_to_garmin_device}, will skip mounting")
        else:
            log.debug("no device mounted yet, will mount...")
            path_to_garmin_device = _wait_for_device_and_mount()

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


def _wait_for_device_and_mount() -> str:
    """
    Function to be called whenever a garmin device is connected via USB. Since it takes a moment for the device to be
    accessible and ready to be mounted we need to wait until the `lsusb` command has "Garmin International" in its
    output.
    """
    if not garmin_device_connected():
        raise FailedToMountDevice("Expected output of 'lsusb' to contain string 'Garmin'.")
    log.debug("checking device to be ready for mount...")
    for n in range(RETRIES):
        lsusb = _get_lsusb_output()
        if DEVICE_READY_STRING in lsusb and DEVICE_NOT_READY_STRING not in lsusb:
            path = _get_path_to_device(lsusb)
            log.debug("device seems to be ready for mount, mounting...")
            device_type = _determine_type_and_mount(path)
            if device_type == DeviceType.MTP and _device_type_is_mounted(EXPECTED_MTP_DEVICE_PATH):
                log.info(f"successfully mounted device at: {EXPECTED_MTP_DEVICE_PATH}")
                return EXPECTED_MTP_DEVICE_PATH
            elif device_type == DeviceType.BLOCK and _device_type_is_mounted(EXPECTED_BLOCK_DEVICE_PATH):
                log.info(f"successfully mounted device at: {EXPECTED_BLOCK_DEVICE_PATH}")
                return EXPECTED_BLOCK_DEVICE_PATH
            else:
                log.warning(
                    f"unable to mount device of type: {device_type}, will retry {RETRIES - (n+1)} more time(s)..."
                )
        else:
            log.info(f"device is not ready for mounting yet, waiting {WAIT} seconds...")
            time.sleep(WAIT)
    log.warning(f"could not mount device within time window of {RETRIES * WAIT} seconds.")
    raise FailedToMountDevice(f"Unable to mount device after {RETRIES} retries, with {WAIT}s delay each.")


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


def _mount_device_using_gio(path: str) -> None:
    subprocess.check_output(["gio", "mount", "-d", path]).decode("utf-8").rstrip()


def _mount_device_using_pmount(path: str) -> None:
    subprocess.check_output(["pmount", path, "garmin"]).decode("utf-8")


def garmin_device_connected() -> bool:
    try:
        lsusb = _get_lsusb_output()
    except (FileNotFoundError, subprocess.CalledProcessError):
        raise FailedToMountDevice(
            "No 'lsusb' command available on your system. Workoutizer will not be able to mount your Garmin device"
        )
    if "Garmin" in lsusb:
        return True
    else:
        return False


def _get_lsusb_output() -> str:
    return subprocess.check_output("lsusb").decode("utf8")


def _determine_type_and_mount(path: str) -> DeviceType:
    device_type, path = _determine_device_type(path)
    log.debug(f"device at path {path} is of type {device_type}")
    try:
        if device_type == DeviceType.MTP:
            _mount_device_using_gio(path)
        elif device_type == DeviceType.BLOCK:
            _mount_device_using_pmount(path)
        return device_type
    except subprocess.CalledProcessError as e:
        raise FailedToMountDevice(f"Execution of mount command failed: {e}")


def _determine_device_type(path: str) -> Tuple[DeviceType, str]:
    log.debug(f"trying to determine device type for device at: {path}...")
    try:
        device_tree = pyudev.Context()
    except ImportError:
        raise FailedToMountDevice("Your system seems to lack the udev utility.")

    # check if device is of type MTP
    if _is_of_type_mtp(device_tree):
        return DeviceType.MTP, path

    # check if device is of type BLOCK
    block_device_path = _get_block_device_path(device_tree, path)
    if block_device_path:
        return DeviceType.BLOCK, block_device_path
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


def _device_type_is_mounted(expected_path: Path) -> bool:
    return expected_path.is_dir() and any(expected_path.iterdir())


def _get_path_of_mounted_device() -> Union[bool, str]:
    log.debug("sanity check to see if a device is already mounted...")
    if _device_type_is_mounted(EXPECTED_MTP_DEVICE_PATH):
        return str(EXPECTED_MTP_DEVICE_PATH.absolute())
    elif _device_type_is_mounted(EXPECTED_BLOCK_DEVICE_PATH):
        return str(EXPECTED_BLOCK_DEVICE_PATH.absolute())
    else:
        return False
