import datetime

import pytest

from wkz.file_helper.auto_naming import (
    _get_daytime_name,
    _get_sport_name,
    _get_coordinate_not_null,
)


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
