import os
import datetime

import pytest

from wizer.file_helper.auto_naming import (
    _get_location_name,
    _get_daytime_name,
    _get_sport_name,
    _get_coordinate_not_null,
)
from wizer.apps import run_parser
from wizer import models


def test__get_location_name():
    coordinate = (48.1234, 8.9123)
    location_name = _get_location_name(coordinate=coordinate)
    assert location_name == "Heidenstadt"

    coordinate = (49.47950, 8.47102)
    location_name = _get_location_name(coordinate=coordinate)
    assert location_name == "Mannheim"

    # this would raise an exception in geopy so we expect to get None
    coordinate = (-90, 90)
    location_name = _get_location_name(coordinate=coordinate)
    assert location_name is None

    # also this would raise an exception, however this
    # is not the location which is supposed to fail
    coordinate = (-1000, 90)
    location_name = _get_location_name(coordinate=coordinate)
    assert location_name is None


def test__get_daytime_name():
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 0)) == "Late Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 1)) == "Late Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 2)) == "Late Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 3)) == "Late Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 4)) == "Late Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 5)) == "Early Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 6)) == "Early Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 7)) == "Early Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 8)) == "Early Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 9)) == "Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 10)) == "Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 11)) == "Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 12)) == "Morning"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 13)) == "Noon"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 14)) == "Noon"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 15)) == "Noon"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 16)) == "Noon"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 17)) == "Evening"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 18)) == "Evening"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 19)) == "Evening"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 20)) == "Evening"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 21)) == "Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 22)) == "Night"
    assert _get_daytime_name(datetime.datetime(2020, 1, 1, 23)) == "Night"

    with pytest.raises(ValueError, match="hour must be in 0..23"):
        assert _get_daytime_name(datetime.datetime(2020, 1, 1, 24)) == "Late Night"


def test__get_sport_name():
    assert _get_sport_name("running") == "Running"
    assert _get_sport_name("unknown") == "Sport"
    assert _get_sport_name("KAYAKING") == "Kayaking"
    assert _get_sport_name("----") == "----"


def test__get_coordinate_not_null():
    assert _get_coordinate_not_null("[null, null, 48.123, null, null, 48.234]") == 48.123
    assert _get_coordinate_not_null("[null, null]") is None


def test_automatic_naming_of_activity__gpx_with_coordinates(db, test_data_dir):
    path_to_trace = os.path.join(test_data_dir, "example.gpx")
    run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Evening Running in Heidelberg"


def test_automatic_naming_of_activity__fit_with_coordinates(db, test_data_dir):
    path_to_trace = os.path.join(test_data_dir, "hike_with_coordinates.fit")
    run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Evening Walking in Ringgenberg (BE)"


def test_automatic_naming_of_activity__fit_no_coordinates(db, test_data_dir):
    path_to_trace = os.path.join(test_data_dir, "swim_no_coordinates.fit")
    run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Noon Swimming"
