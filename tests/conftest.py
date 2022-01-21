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
def fit_file():  # sport = running
    return "2019-09-14-17-22-05.fit"


@pytest.fixture
def fit_file_a():  # sport = running
    return "2019-09-18-16-02-35.fit"


@pytest.fixture
def fit_file_b():  # sport = running
    return "2019-09-25-16-15-53.fit"


@pytest.fixture
def fit_file_c():  # sport = walking
    return "2020-08-20-09-34-33.fit"


@pytest.fixture
def fit_file_d():  # sport = walking
    return "2020-08-28-11-57-10.fit"


@pytest.fixture
def fit_file_e():  # sport = running
    return "2020-08-31-17-41-11.fit"


@pytest.fixture
def fit_file_f():  # sport = cycling
    return "2020-10-25-10-54-06.fit"


@pytest.fixture
def fit_file_g():  # sport = cycling
    return "cycling_bad_schandau.fit"


@pytest.fixture
def fit_file_h():  # sport = hiking
    return "hike_with_coordinates_muggenbrunn.fit"


@pytest.fixture
def gpx_file():  # sport = cycling
    return "cycling_walchensee.gpx"


MOCKED_WAIT = 0.1
MOCKED_RETRY = 3


@pytest.fixture
def mock_mount_waiting_time(monkeypatch) -> None:
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


@pytest.fixture
def mock_expected_device_paths(monkeypatch, tmp_path) -> None:
    from wkz.device import mount

    # mock expected device paths in order to test these to be real dirs
    mtp_path = tmp_path / "mtp"
    mtp_path.mkdir()
    p = mtp_path / "some_mtp_file.fit"
    p.write_text("foo")
    monkeypatch.setattr(mount, "EXPECTED_MTP_DEVICE_PATH", mtp_path)

    block_path = tmp_path / "block"
    block_path.mkdir()
    p = block_path / "some_block_file.fit"
    p.write_text("baa")
    monkeypatch.setattr(mount, "EXPECTED_BLOCK_DEVICE_PATH", block_path)
