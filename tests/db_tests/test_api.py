import os
import subprocess

import pytest
from rest_framework.test import APIClient

from wkz import models
from wkz.file_helper import fit_collector


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


def test_mount_device__failure(db, monkeypatch, client):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return "dummy-string"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 500


@pytest.mark.parametrize("mock_dev", ["BLOCK", "MTP"])
def test_mount_device__success(db, monkeypatch, tmpdir, client, mock_dev, caplog):
    # prepare settings
    target_dir = tmpdir.mkdir("tracks")
    settings = models.get_settings()
    settings.path_to_garmin_device = tmpdir  # source
    settings.path_to_trace_dir = target_dir  # target
    settings.save()

    # mock output of subprocess ("lsusb") to prevent function from failing
    def check_output(dummy):
        return "dummy\nstring\nsome\ncontent\ncontaining\nGarmin"

    monkeypatch.setattr(subprocess, "check_output", check_output)

    # mock output of actual mounting command (with actual gio output text)
    path_to_device = "/some/dummy/path/to/device"

    def mount(path):
        return f"Mounted /dev/bus/usb/001/004 at {path_to_device}"

    monkeypatch.setattr(fit_collector, "_mount_device_using_gio", mount)
    monkeypatch.setattr(fit_collector, "_mount_device_using_pmount", mount)

    # mock output of _find_device_type
    def _find_device_type(bus, dev):
        if mock_dev == "MTP":
            return ("MTP", "/dev/bus/usb/001/002")
        elif mock_dev == "BLOCK":
            return ("BLOCK", "/dev/sda")

    monkeypatch.setattr(fit_collector, "_find_device_type", _find_device_type)

    # create directory to import the fit files from
    fake_device_dir = os.path.join(tmpdir, "mtp:host", "Primary", "GARMIN", "Activity")
    os.makedirs(fake_device_dir)

    res = client.post("/mount-device/")
    assert f"successfully mounted device at: {path_to_device}" in caplog.text
    assert res.status_code == 200
