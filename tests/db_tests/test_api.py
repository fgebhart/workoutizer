import logging
import subprocess

import pytest
from rest_framework.test import APIClient

from tests.unit_tests.device.test_mount import lsusb_ready_to_be_mounted_device
from wkz.device import mount


@pytest.fixture
def client():
    yield APIClient()


def test_missing_endpoint(client):
    res = client.post("/this-endpoint-is-not-implemented/")

    # having a redirection in place for all 404s will actually give as a 302 "Found (Previously "Moved temporarily")"
    assert res.status_code == 302


def test_stop(client):
    with pytest.raises(KeyboardInterrupt):
        client.post("/stop/")


def test_mount_device__no_device_connected(db, monkeypatch, client):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return b"dummy-string"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 200
    assert res.content.decode("utf8") == '"No Garmin device connected."'


def test_mount_device__device_connected(db, monkeypatch, client, mock_mount_waiting_time):
    from workoutizer import settings as django_settings

    def task(func):
        return func

    # first mock decorator HUEY.task with dummy function
    monkeypatch.setattr(django_settings.HUEY, "task", task)

    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return b"dummy-string-containing-Garmin"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 200
    assert res.content.decode("utf8") == '"Found device, will mount and collect fit files."'


@pytest.mark.parametrize("mock_dev", ["BLOCK", "MTP"])
def test_mount_device__success(db, monkeypatch, tmpdir, client, mock_dev, caplog, _mock_lsusb):
    caplog.set_level(logging.DEBUG, logger="wkz.api")

    # mock output of subprocess ("lsusb") to prevent function from failing
    _mock_lsusb(lsusb_ready_to_be_mounted_device)

    # mock output of actual mounting command (with actual gio output text)
    path_to_device = tmpdir

    def mount_cmd(path):
        return f"Mounted /dev/bus/usb/001/004 at {path_to_device}"

    monkeypatch.setattr(mount, "_mount_device_using_gio", mount_cmd)
    monkeypatch.setattr(mount, "_mount_device_using_pmount", mount_cmd)

    # mock output of _determine_device_type
    def _determine_device_type(path):
        if mock_dev == "MTP":
            return "MTP"
        elif mock_dev == "BLOCK":
            return "BLOCK"

    monkeypatch.setattr(mount, "_determine_device_type", _determine_device_type)

    # mount device (no new fit files collected)
    res = client.post("/mount-device/")
    assert "received POST request for mounting garmin device" in caplog.text
    assert "found connected garmin device" in caplog.text
    assert res.status_code == 200
    assert res.content.decode("utf8") == '"Found device, will mount and collect fit files."'
