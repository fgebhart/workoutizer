import os
import datetime

import pytest
import pytz
from django.utils import timezone
from django.conf import settings as django_settings

from wizer.models import Settings, Sport, Activity


@pytest.fixture
def settings(db):
    settings = Settings(
        path_to_trace_dir="/home/pi/traces/",
        path_to_garmin_device="/home/pi/traces/",
        file_checker_interval=90,
        number_of_days=30,
        reimporter_updates_all=False,
        delete_files_after_import=False,
    )
    settings.save()
    return settings


@pytest.fixture
def sport(db):
    sport = Sport(name='Some Crazy Stuff', color='red', icon='Bike')
    sport.save()
    return sport


@pytest.fixture
def activity(db, sport):
    activity = Activity(
        name='Running',
        sport=sport,
        date=timezone.now().replace(tzinfo=pytz.timezone(django_settings.TIME_ZONE)),
        duration=datetime.timedelta(minutes=30),
        distance=5.2,
        description="some super sport",
    )
    activity.save()
    return activity


@pytest.fixture
def ip_port():
    return "192.168.0.108:8000"


@pytest.fixture
def wkz_service_path():
    return '/etc/systemd/system/wkz.service'


@pytest.fixture
def wkz_mount_service_path():
    return '/etc/systemd/system/wkz_mount.service'


@pytest.fixture
def udev_rule_dir():
    return '/etc/udev/rules.d'


@pytest.fixture
def udev_rule_path(udev_rule_dir):
    return f'{udev_rule_dir}/device_mount.rules'


@pytest.fixture
def vendor_id():
    return '091e'


@pytest.fixture
def product_id():
    return '4b48'
