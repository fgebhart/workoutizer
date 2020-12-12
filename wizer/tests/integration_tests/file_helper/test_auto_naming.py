import datetime

import pytest

from wizer.file_helper.auto_naming import _get_location_name, _get_daytime_name


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
