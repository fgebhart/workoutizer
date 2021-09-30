import logging
import subprocess
import time
from typing import Tuple

import pyudev

RETRIES = 10
WAIT = 10
DEVICE_READY_STRING = "Garmin International"
DEVICE_NOT_READY_STRING = "(various models)"


log = logging.getLogger(__name__)


class FailedToMountDevice(Exception):
    pass


def wait_for_device_and_mount() -> str:
    """
    Function to be called whenever a garmin device is connected via USB. Since it takes a moment for the device to be
    accessible and ready to be mounted we need to wait until the `lsusb` command has "Garmin International" in its
    output.
    """
    time.sleep(2)
    try:
        lsusb = _get_lsusb_output()
    except FileNotFoundError:
        raise FailedToMountDevice("Failed to call 'lsusb' command.")
    assert "Garmin" in lsusb

    log.debug("checking device to be ready for mount...")
    for _ in range(RETRIES):
        lsusb = _get_lsusb_output()
        if DEVICE_READY_STRING in lsusb and DEVICE_NOT_READY_STRING not in lsusb:
            dev, bus, path = _get_dev_bus_and_path_to_device(lsusb)
            log.debug("device seems to be ready for mount, mounting...")
            (dev_type, path) = _find_device_type(bus, dev)
            log.debug(f"device at path {path} is of type {dev_type}")
            if dev_type == "MTP":
                mount_output = _mount_device_using_gio(path)
            elif dev_type == "BLOCK":
                mount_output = _mount_device_using_pmount(path)
            if "Mounted" in mount_output:
                mounted_path = _get_mounted_path(mount_output)
                # TODO also trigger fit collector once mounted.
                log.info(f"successfully mounted device at: {mounted_path}")
                return mounted_path
            else:
                raise FailedToMountDevice(f"Mount command did not return expected output: {mount_output}")
        else:
            log.debug(f"device is not ready for mounting yet, waiting {WAIT} seconds...")
            time.sleep(WAIT)
    log.warning(f"could not mount device within time window of {RETRIES * WAIT} seconds.")
    raise FailedToMountDevice(f"Unable to mount device with after {RETRIES} retries, with {WAIT}s delay each.")


def _get_mounted_path(mount_output: str) -> str:
    if "Mounted" not in mount_output:
        raise FailedToMountDevice(
            f"Output of mount command does not look as expected: {mount_output}. Expected to contain 'Mounted'."
        )
    path_start = mount_output.find("at")
    mount_path = mount_output[path_start + 3 :]
    return mount_path


def _get_dev_bus_and_path_to_device(lsusb_output: str) -> Tuple[str, str, str]:
    lsusb_output = str(lsusb_output).split("\\n")
    path = None
    for line in lsusb_output:
        if DEVICE_READY_STRING in line:
            bus_start = line.find("Bus") + 4
            bus = line[bus_start : bus_start + 3]
            device_start = line.find("Device") + 7
            dev = line[device_start : device_start + 3]
            path = f"/dev/bus/usb/{bus}/{dev}"
    if path is None:
        raise FileNotFoundError(f"Could not find {DEVICE_READY_STRING} in lsusb output.")
    else:
        return dev, bus, path


def _mount_device_using_gio(path: str) -> str:
    return subprocess.check_output(["gio", "mount", "-d", path]).decode("utf-8").rstrip()


def _mount_device_using_pmount(path: str) -> str:
    subprocess.check_output(["pmount", path, "garmin"]).decode("utf-8")
    # pmount does not return anything, assume command to be successful and return expected string
    return "Mounted at /media/garmin"


def _get_lsusb_output() -> str:
    return subprocess.check_output("lsusb").decode("utf8")


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
                if vendor_id == device.get("ID_VENDOR_ID"):
                    return ("BLOCK", device.get("DEVNAME"))
    # raise error in case no device type was found
    raise FailedToMountDevice(f"Could not determine device type for bus: {bus}, dev: {dev}")
