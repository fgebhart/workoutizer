import shutil
from py._path.local import LocalPath
from typing import List

import pytest

from workoutizer import settings as django_settings
from wkz.file_importer import copy_demo_fit_files_to_track_dir
from wkz import models


class FakeDevice:
    def __init__(self, mount_path: LocalPath, device_dir, activity_dir: str, activity_files):
        self.mount_path = mount_path
        self.device_path = self.mount_path / device_dir
        self.activity_path_on_device = self.device_path / activity_dir
        self.mounted = False
        self.activity_files = activity_files

    def mount(self):
        # create directories for activities
        if not self.mounted:
            print("mounting fake device...")
            self.activity_path_on_device.mkdir(parents=True)
            if self.activity_files:
                # copy activity files into activity dir
                copy_demo_fit_files_to_track_dir(
                    source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
                    targe_dir=self.activity_path_on_device,
                    list_of_files_to_copy=self.activity_files,
                )
            self.mounted = True

    def unmount(self):
        if self.mounted:
            print("unmounting fake device...")
            shutil.rmtree(self.device_path)
            self.mounted = False


@pytest.fixture
def fake_device(tmp_path, device_dir, activity_dir):
    settings = models.get_settings()

    mount_path = tmp_path / "mount_path"
    mount_path.mkdir()
    assert mount_path.is_dir()
    settings.path_to_garmin_device = mount_path

    trace_dir = tmp_path / "trace_dir"
    trace_dir.mkdir()
    assert trace_dir.is_dir()
    settings.path_to_trace_dir = trace_dir

    settings.save()

    def _get_device(activity_files: List[str], device_dir: str = device_dir, activity_dir: str = activity_dir):
        return FakeDevice(
            mount_path=settings.path_to_garmin_device,
            device_dir=device_dir,
            activity_dir=activity_dir,
            activity_files=activity_files,
        )

    return _get_device


@pytest.fixture
def fit_file():
    return "2019-09-14-17-22-05.fit"


@pytest.fixture
def fit_file_a():
    return "2019-09-18-16-02-35.fit"


@pytest.fixture
def fit_file_b():
    return "2019-09-25-16-15-53.fit"


@pytest.fixture
def device_dir():
    return "mtp:host_DEVICE"


@pytest.fixture
def activity_dir():
    return "Primary/GARMIN/Activity"
