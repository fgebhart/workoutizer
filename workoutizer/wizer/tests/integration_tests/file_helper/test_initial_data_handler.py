import os
import datetime

import pytz

from workoutizer import settings
from wizer.models import Settings, Sport, Activity
from wizer.file_helper.initial_data_handler import _insert_current_date_into_gpx, insert_settings_and_sports_to_model, \
    insert_activities_to_model


def test__insert_current_date_into_gpx(gpx_parser):
    path_to_test_data_dir = os.path.join(settings.BASE_DIR, "wizer/tests/integration_tests/data/")
    test_file = "template_example.gpx"
    path_to_output_dir = os.path.join(path_to_test_data_dir, "tested_data")
    date = datetime.datetime(2020, 4, 1, tzinfo=pytz.utc)
    _insert_current_date_into_gpx(
        gpx_file_name=test_file,
        source_path=path_to_test_data_dir,
        target_path=path_to_output_dir,
        strf_timestamp=date)
    parser = gpx_parser(path=os.path.join(path_to_output_dir, test_file))
    assert parser.file_name == test_file
    assert parser.date == date


def test_insert_settings_and_sports_to_model(db):
    # assert that there are no settings
    assert Settings.objects.count() == 0

    # insert settings and sports
    insert_settings_and_sports_to_model(Settings, Sport)
    assert Settings.objects.count() == 1
    assert Settings.objects.get(pk=1).number_of_days == 30

    # check that at least one sport object is present
    assert Sport.objects.count() > 0


def test_insert_activities_to_model(db):
    # assert that there are no activities
    assert Activity.objects.count() == 0

    # can insert activities only in the case of present sports
    insert_settings_and_sports_to_model(Settings, Sport)
    # no insert activities
    insert_activities_to_model(Sport, Activity)
    assert Activity.objects.count() > 0
