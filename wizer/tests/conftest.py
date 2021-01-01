import os
import datetime

import pytest

from wizer.models import BestSection, Settings, Sport, Activity, Traces, get_settings
from workoutizer import settings as django_settings


@pytest.fixture
def settings(db):
    settings = Settings(
        path_to_trace_dir="/home/pi/traces/",
        path_to_garmin_device="/home/pi/traces/",
        number_of_days=30,
        reimporter_updates_all=False,
        delete_files_after_import=False,
    )
    settings.save()
    return settings


@pytest.fixture
def sport(db):
    sport = Sport(name="Cycling", color="red", icon="Bike")
    sport.save()
    return sport


@pytest.fixture
def trace_file(db):
    trace = Traces(
        path_to_file="some/path/to/file.gpx",
        file_name="file.gpx",
        md5sum="4c1185c55476269b442f424a9d80d964",
        latitude_list="[49.47972273454071, 49.47972273454071]",
        longitude_list="[8.47357001155615, 8.47357001155615]",
        calories=123,
    )
    trace.save()
    return trace


@pytest.fixture
def activity(db, sport, trace_file):
    activity = Activity(
        name="Evening Cycling along the River",
        sport=sport,
        date=datetime.datetime(2020, 7, 7),
        duration=datetime.timedelta(minutes=30),
        distance=5.2,
        description="some super sport",
        trace_file=trace_file,
    )
    activity.save()
    return activity


@pytest.fixture
def insert_best_section(db, activity):
    def _create_section(max_value: float):
        best_section = BestSection(
            activity=activity,
            section_type="fastest",
            section_distance=1,
            start_index=5,
            end_index=517,
            max_value=max_value,
        )
        best_section.save()
        return best_section

    return _create_section


@pytest.fixture
def ip_port():
    return "192.168.0.108:8000"


@pytest.fixture
def wkz_service_path():
    return "/etc/systemd/system/wkz.service"


@pytest.fixture
def wkz_mount_service_path():
    return "/etc/systemd/system/wkz_mount.service"


@pytest.fixture
def udev_rule_dir():
    return "/etc/udev/rules.d"


@pytest.fixture
def udev_rule_path(udev_rule_dir):
    return f"{udev_rule_dir}/device_mount.rules"


@pytest.fixture
def vendor_id():
    return "091e"


@pytest.fixture
def product_id():
    return "4b48"


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def demo_data_dir():
    return django_settings.INITIAL_TRACE_DATA_DIR


@pytest.fixture
def tracks_in_tmpdir(tmpdir):
    target_dir = tmpdir.mkdir("tracks")
    settings = get_settings()
    settings.path_to_trace_dir = target_dir
    settings.save()
