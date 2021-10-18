import os
import subprocess

import pytest

from workoutizer import settings as django_settings


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def demo_data_dir():
    return django_settings.INITIAL_TRACE_DATA_DIR


@pytest.fixture(autouse=True)
def keep_tracks_dir_clean():
    """
    Fixture to ensure no test adds activity files to the default tracks dir.
    """
    if os.path.isdir(django_settings.TRACKS_DIR):
        num_before = os.listdir(django_settings.TRACKS_DIR)
        yield
        num_after = os.listdir(django_settings.TRACKS_DIR)
        assert num_before == num_after
    else:
        yield


@pytest.fixture
def fit_file():
    return "2019-09-14-17-22-05.fit"


@pytest.fixture
def fit_file_a():
    return "2019-09-18-16-02-35.fit"


@pytest.fixture
def fit_file_b():
    return "2019-09-25-16-15-53.fit"


MOCKED_WAIT = 0.1
MOCKED_RETRY = 3


@pytest.fixture
def mock_mount_waiting_time(monkeypatch):
    from wkz.device import mount

    # mock number of retries and waiting time to speed up test execution
    monkeypatch.setattr(mount, "WAIT", MOCKED_WAIT)
    monkeypatch.setattr(mount, "RETRIES", MOCKED_RETRY)


@pytest.fixture
def _mock_lsusb(monkeypatch) -> None:
    # mocking the subprocess call to `lsusb` to get the desired outout
    def mock(output: str) -> None:
        def lsusb_output(foo) -> bytes:
            return bytes(output, "utf8")

        return monkeypatch.setattr(subprocess, "check_output", lsusb_output)

    return mock
