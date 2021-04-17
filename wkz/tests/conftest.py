import datetime
import os

import pytest
import pytz
from django.core.management import call_command

from workoutizer import settings as django_settings
from wkz.file_importer import (
    import_activity_files,
    prepare_import_of_demo_activities,
    copy_demo_fit_files_to_track_dir,
)
from wkz import models


@pytest.fixture
def flush_db(db):
    call_command("flush", verbosity=0, interactive=False)


@pytest.fixture
def settings(db):
    settings = models.Settings(
        path_to_trace_dir="/home/pi/traces/",
        path_to_garmin_device="/home/pi/traces/",
        number_of_days=30,
        delete_files_after_import=False,
    )
    settings.save()
    return settings


@pytest.fixture
def sport(db):
    sport = models.Sport(name="Cycling", color="red", icon="Bike")
    sport.save()
    return sport


@pytest.fixture
def trace_file(db):
    trace = models.Traces(
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
    activity = models.Activity(
        name="Evening Cycling along the River",
        sport=sport,
        date=datetime.datetime(2020, 7, 7, tzinfo=pytz.timezone(django_settings.TIME_ZONE)),
        duration=datetime.timedelta(minutes=30),
        distance=5.2,
        description="some super sport",
        trace_file=trace_file,
    )
    activity.save()
    return activity


@pytest.fixture
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def demo_data_dir():
    return django_settings.INITIAL_TRACE_DATA_DIR


@pytest.fixture
def tracks_in_tmpdir(tmpdir):
    target_dir = tmpdir.mkdir("tracks")
    settings = models.get_settings()
    settings.path_to_trace_dir = target_dir
    settings.save()


@pytest.fixture
def import_demo_data(db, tracks_in_tmpdir):
    prepare_import_of_demo_activities(models)
    assert models.Sport.objects.count() == 5
    assert models.Settings.objects.count() == 1

    import_activity_files(models, importing_demo_data=True)
    assert models.Activity.objects.count() > 1


@pytest.fixture
def import_one_activity(db, tracks_in_tmpdir):
    models.get_settings()
    assert models.Settings.objects.count() == 1

    def _copy_activity(file_name: str):
        copy_demo_fit_files_to_track_dir(
            source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
            targe_dir=models.get_settings().path_to_trace_dir,
            list_of_files_to_copy=[file_name],
        )
        import_activity_files(models, importing_demo_data=False)
        assert models.Activity.objects.count() == 1

    return _copy_activity


@pytest.fixture
def insert_sport(db):
    def _create_sport(name="Cycling", icon="bicycle"):
        sport = models.Sport(name=name, color="red", icon=icon)
        sport.save()
        return sport

    return _create_sport


@pytest.fixture
def insert_activity(db, sport):
    def _create_activity(
        name: str = "Evening Cycling along the River",
        evaluates_for_awards: bool = True,
        sport=sport,
        date: datetime.datetime = datetime.datetime(2020, 7, 7, tzinfo=pytz.timezone(django_settings.TIME_ZONE)),
        duration: datetime.timedelta = datetime.timedelta(minutes=30),
    ):
        activity = models.Activity(
            name=name,
            sport=sport,
            date=date,
            duration=duration,
            distance=5.2,
            description="some super activity",
            evaluates_for_awards=evaluates_for_awards,
        )
        activity.save()
        return activity

    return _create_activity


@pytest.fixture
def insert_best_section(db, activity, insert_activity):
    def _create_section(max_value: float):
        best_section = models.BestSection(
            activity=insert_activity(),  # always use a new activity
            kind="fastest",
            distance=1,
            start=5,
            end=517,
            max_value=max_value,
        )
        best_section.save()
        return best_section

    return _create_section
