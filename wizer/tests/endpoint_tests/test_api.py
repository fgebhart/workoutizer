import subprocess

from rest_framework.test import APIClient
import pytest


def test_missing_endpoint():
    client = APIClient()
    res = client.post("/this-endpoint-is-not-implemented/")

    assert res.status_code == 404


def test_stop():
    client = APIClient()
    with pytest.raises(KeyboardInterrupt):
        client.post("/stop/")


def test_mount_device(db, monkeypatch):
    # mock output of subprocess to prevent function from failing
    def dummy_output(dummy):
        return "dummy-string"

    monkeypatch.setattr(subprocess, "check_output", dummy_output)

    client = APIClient()
    res = client.post("/mount-device/")

    # mounting a device is barely possible in testing, thus at least assert that the endpoint returns 500
    assert res.status_code == 500
