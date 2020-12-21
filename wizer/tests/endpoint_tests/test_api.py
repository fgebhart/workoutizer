import os
import subprocess

from rest_framework.test import APIClient
import pytest

from wizer.file_helper import fit_collector
from wizer import models


def test_missing_endpoint():
    client = APIClient()
    res = client.post("/this-endpoint-is-not-implemented/")

    assert res.status_code == 404


def test_stop():
    client = APIClient()
    with pytest.raises(KeyboardInterrupt):
        client.post("/stop/")


def test_mount_device__not_importing(db, monkeypatch):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return "dummy-string"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)

    client = APIClient()
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 500


def test_mount_device__importing(db, monkeypatch, test_data_dir):
    # prepare settings
    settings = models.Settings(
        path_to_trace_dir=os.path.join(test_data_dir, "tested_data"),
        path_to_garmin_device=test_data_dir,
    )
    settings.save()

    # mock output of subprocess to prevent function from failing
    def dummy_output():
        return "dummy-string"

    monkeypatch.setattr(fit_collector, "try_to_mount_device", dummy_output)

    client = APIClient()
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 200
