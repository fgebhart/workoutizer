import os

import pytest

from workoutizer import settings as django_settings


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
