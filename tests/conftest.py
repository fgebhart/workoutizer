import os

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
