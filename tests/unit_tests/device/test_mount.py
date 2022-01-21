import logging
import subprocess
from pathlib import Path

import pytest

from wkz.device import mount
from wkz.device.mount import DeviceType

lsusb_ready_to_be_mounted_device = """
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 004: ID 091e:4b48 Garmin International
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
"""

lsusb_no_garmin_device_at_all = """
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
"""

lsusb_device_not_ready_to_be_mounted = """
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 091e:0003 Garmin International GPS (various models)
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
"""


def test__get_lsusb_output(_mock_lsusb):
    # without mocking it will fail since lsusb does not exist in docker container
    with pytest.raises((FileNotFoundError, subprocess.CalledProcessError)):
        mount._get_lsusb_output()

    _mock_lsusb(output=lsusb_ready_to_be_mounted_device)
    output = mount._get_lsusb_output()
    assert "Garmin International" in output
    assert "091e:4b48" in output

    _mock_lsusb(output="dummy string")
    output = mount._get_lsusb_output()
    assert output == "dummy string"


def test__get_path_to_device__passes():
    assert mount._get_path_to_device(lsusb_ready_to_be_mounted_device) == "/dev/bus/usb/001/004"


def test__get_path_to_device__no_device():
    with pytest.raises(AssertionError):
        mount._get_path_to_device("dummy string")


def test__get_path_to_device__real_world_string():
    lsusb = """
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 006: ID 091e:4b48 Garmin International
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    """
    assert mount._get_path_to_device(lsusb) == "/dev/bus/usb/001/006"


@pytest.mark.parametrize("mock_dev", [DeviceType.BLOCK, DeviceType.MTP])
def test_wait_for_device_and_mount(
    monkeypatch, _mock_lsusb, caplog, mock_dev, mock_mount_waiting_time, mock_expected_device_paths
):
    caplog.set_level(logging.DEBUG, logger="wkz.device.mount")

    # try to mount device where no device is connected at all
    _mock_lsusb(lsusb_no_garmin_device_at_all)
    with pytest.raises(mount.FailedToMountDevice, match="Expected output of 'lsusb' to contain string 'Garmin'."):
        mount._wait_for_device_and_mount()

    # try to mount device where device is not ready
    _mock_lsusb(lsusb_device_not_ready_to_be_mounted)
    with pytest.raises(mount.FailedToMountDevice):
        mount._wait_for_device_and_mount()

    from tests.conftest import MOCKED_RETRY, MOCKED_WAIT

    assert f"device is not ready for mounting yet, waiting {MOCKED_WAIT} seconds..." in caplog.text
    assert f"could not mount device within time window of {MOCKED_WAIT * MOCKED_RETRY} seconds." in caplog.text

    # mock output of actual mounting command (with actual gio output text)
    if mock_dev == DeviceType.BLOCK:
        path_to_device = mount.EXPECTED_BLOCK_DEVICE_PATH
    elif mock_dev == DeviceType.MTP:
        path_to_device = mount.EXPECTED_MTP_DEVICE_PATH

    # mock output of _determine_device_type
    def _determine_device_type(path):
        if mock_dev == DeviceType.MTP:
            return DeviceType.MTP, path
        elif mock_dev == DeviceType.BLOCK:
            return DeviceType.BLOCK, path

    monkeypatch.setattr(mount, "_determine_device_type", _determine_device_type)

    # try to mount device which is ready to be mounted from the beginning on
    _mock_lsusb(lsusb_ready_to_be_mounted_device)
    path = mount._wait_for_device_and_mount()

    assert "device seems to be ready for mount, mounting..." in caplog.text
    assert path == path_to_device


@pytest.mark.parametrize("mock_dev", [DeviceType.BLOCK, DeviceType.MTP])
def test_wait_for_device_and_mount__first_not_but_then_ready(
    mock_dev, tmp_path, mock_mount_waiting_time, monkeypatch, caplog, mock_expected_device_paths
):
    caplog.set_level(logging.DEBUG, logger="wkz.device.mount")

    # store number of function calls to a file to simulate the repeated call to the lsusb output function
    counter_file = tmp_path / "counter.txt"
    counter_file.write_text("0")

    def lsusb_output() -> str:
        counter = int(counter_file.read_text())
        counter_file.write_text(str(counter + 1))
        if counter > 2:
            return lsusb_ready_to_be_mounted_device
        else:
            return lsusb_device_not_ready_to_be_mounted

    monkeypatch.setattr(mount, "_get_lsusb_output", lsusb_output)

    path = "/dev/bus/usb/001/004"

    def mount_cmd(path):
        return f"Mounted device at {path}"

    # mock output of _find_device_type
    if mock_dev == DeviceType.MTP:
        monkeypatch.setattr(mount, "_mount_device_using_gio", mount_cmd)

    elif mock_dev == DeviceType.BLOCK:
        monkeypatch.setattr(mount, "_mount_device_using_pmount", mount_cmd)

    def _determine_device_type(path):
        return mock_dev, path

    monkeypatch.setattr(mount, "_determine_device_type", _determine_device_type)

    # call function to be tested
    mount_path = mount._wait_for_device_and_mount()

    assert "device is not ready for mounting yet, waiting 0.1 seconds..." in caplog.text
    assert "device seems to be ready for mount, mounting..." in caplog.text
    assert f"device at path {path} is of type {mock_dev}" in caplog.text
    assert f"successfully mounted device at: {mount_path}" in caplog.text


def test_garmin_device_connected(_mock_lsusb):
    _mock_lsusb(output=lsusb_ready_to_be_mounted_device)
    assert mount.garmin_device_connected() is True

    _mock_lsusb(output=lsusb_no_garmin_device_at_all)
    assert mount.garmin_device_connected() is False


def test__device_type_is_mounted(tmp_path):
    # neither is path a dir nor does it contain anything
    assert mount._device_type_is_mounted(expected_path=Path("no_path")) is False

    # path is dir but does not contain anything
    assert mount._device_type_is_mounted(expected_path=Path(tmp_path)) is False

    # path is dir and contains a file
    d = tmp_path / "subfolder"
    d.mkdir()
    p = d / "some_file.txt"
    p.write_text("foo")
    assert mount._device_type_is_mounted(expected_path=Path(d)) is True
