import datetime

import pytz
import pytest
from django.core.management import call_command

from workoutizer import settings as django_settings
from wizer.file_importer import (
    import_activity_files,
    prepare_import_of_demo_activities,
    copy_demo_fit_files_to_track_dir,
)
from wizer import models


@pytest.fixture
def flush_db():
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
def insert_best_section(db, activity):
    def _create_section(max_value: float):
        best_section = models.BestSection(
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
def tracks_in_tmpdir(tmpdir):
    target_dir = tmpdir.mkdir("tracks")
    settings = models.get_settings()
    settings.path_to_trace_dir = target_dir
    settings.save()


@pytest.fixture
def import_demo_data(db, tracks_in_tmpdir):
    prepare_import_of_demo_activities(models)
    assert len(models.Sport.objects.all()) == 5
    assert len(models.Settings.objects.all()) == 1

    import_activity_files(models, importing_demo_data=True)
    assert len(models.Activity.objects.all()) > 1


@pytest.fixture
def import_one_activity(db, tracks_in_tmpdir):
    models.get_settings()

    def _copy_activity(file_name: str):
        copy_demo_fit_files_to_track_dir(
            source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
            targe_dir=models.get_settings().path_to_trace_dir,
            list_of_files_to_copy=[file_name],
        )
        assert len(models.Sport.objects.all()) == 1
        assert len(models.Settings.objects.all()) == 1

        return import_activity_files(models, importing_demo_data=False)

    return _copy_activity
