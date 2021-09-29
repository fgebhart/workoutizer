import os
import shutil
import subprocess
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from tests.unit_tests.device.test_mount import lsusb_ready_to_be_mounted_device
from wkz import models
from wkz.device import mount
from workoutizer import settings as django_settings


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


def test_mount_device__failure(db, monkeypatch, client, mock_mount_waiting_time):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return b"dummy-string-containing-Garmin"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 500


@pytest.mark.parametrize("mock_dev", ["BLOCK", "MTP"])
def test_mount_device__success(db, monkeypatch, tmpdir, client, mock_dev, caplog, mock_mount_waiting_time):
    # mock output of subprocess ("lsusb") to prevent function from failing
    def check_output(dummy):
        return lsusb_ready_to_be_mounted_device

    monkeypatch.setattr(subprocess, "check_output", check_output)

    # mock output of actual mounting command (with actual gio output text)
    path_to_device = tmpdir

    def mount_cmd(path):
        return f"Mounted /dev/bus/usb/001/004 at {path_to_device}"

    monkeypatch.setattr(mount, "_mount_device_using_gio", mount_cmd)
    monkeypatch.setattr(mount, "_mount_device_using_pmount", mount_cmd)

    # mock output of _find_device_type
    def _find_device_type(bus, dev):
        if mock_dev == "MTP":
            return ("MTP", "/dev/bus/usb/001/002")
        elif mock_dev == "BLOCK":
            return ("BLOCK", "/dev/sda")

    monkeypatch.setattr(mount, "_find_device_type", _find_device_type)

    # create directory to import the fit files from
    fake_device_dir = os.path.join(path_to_device, "mtp:host", "Primary", "GARMIN", "Activity")
    os.makedirs(fake_device_dir)

    settings = models.get_settings()
    settings.path_to_garmin_device = fake_device_dir
    path_to_trace_dir = tmpdir / "trace_dir"
    settings.path_to_trace_dir = path_to_trace_dir
    settings.save()

    # mount device (no new fit files collected)
    res = client.post("/mount-device/")
    assert f"successfully mounted device at: {path_to_device}" in caplog.text
    assert res.status_code == 200
    assert res.content.decode("utf8") == '"Mounted device and collected 0 fit files."'

    # put a fit file into fake_device_dir and verified it being collected
    fit = "2019-09-18-16-02-35.fit"
    shutil.copy2(os.path.join(django_settings.INITIAL_TRACE_DATA_DIR, fit), fake_device_dir)
    res = client.post("/mount-device/")
    assert f"successfully mounted device at: {path_to_device}" in caplog.text
    assert res.status_code == 200
    assert res.content.decode("utf8") == '"Mounted device and collected 1 fit files."'

    # verify that fit file got collected
    assert Path(path_to_trace_dir / "garmin" / fit).is_file()
