import datetime

import pytz
import pytest
from django.conf import settings
import pandas as pd

from wkz.file_helper.fit_parser import LapData, FITParser
from wkz.best_sections.generic import GenericBestSection


tz = pytz.timezone(settings.TIME_ZONE)


def test__parse_metadata(fit_parser):
    p = fit_parser()
    assert p.file_name == "example.fit"


def test__parse_records(fit_parser):
    p = fit_parser()
    # test single value attributes
    assert p.sport == "running"
    assert p.distance == 5.84
    assert p.duration == datetime.timedelta(seconds=3164)
    assert p.date == datetime.datetime(2019, 9, 14, 16, 15, tzinfo=tz)
    assert p.avg_heart_rate == 130
    assert p.avg_speed == 1.845
    assert p.avg_cadence == 64
    assert p.avg_temperature == 27
    assert p.calories == 432
    assert p.aerobic_training_effect == 2.7
    assert p.anaerobic_training_effect == 0.3
    # check lengths of list attributes
    assert len(p.heart_rate_list) == 1224
    assert len(p.altitude_list) == 1224
    assert len(p.latitude_list) == 1224
    assert len(p.longitude_list) == 1224
    assert len(p.distance_list) == 1224
    assert len(p.cadence_list) == 1224
    assert len(p.temperature_list) == 1224
    assert len(p.speed_list) == 1224
    assert len(p.timestamps_list) == 1224
    # sanity check to see if element in list attributes
    assert 1.605 in p.speed_list
    assert 8.697221484035255 in p.longitude_list
    assert 49.40601873211563 in p.latitude_list
    assert 1.6 in p.distance_list
    assert 248.9 in p.altitude_list
    assert 99 in p.heart_rate_list
    assert 61 in p.cadence_list
    assert 31 in p.temperature_list
    assert 1568467325.0 in p.timestamps_list
    # check laps
    assert p.laps[0] == LapData(
        start_time=datetime.datetime(2019, 9, 14, 15, 22, 5, tzinfo=tz),
        end_time=datetime.datetime(2019, 9, 14, 15, 29, 52, tzinfo=tz),
        elapsed_time=datetime.timedelta(seconds=465, microseconds=90000),
        distance=1000.0,
        start_lat=49.405793594196446,
        start_long=8.694087238982322,
        end_long=8.696012729778888,
        end_lat=49.40549436025322,
        trigger="distance",
        speed=2.15,
    )


def test_set_min_max_values(fit_parser, monkeypatch):
    # mock away post processing in order to test before and after state
    def post_process(baz):
        return "foo"

    monkeypatch.setattr(FITParser, "_post_process_data", post_process)

    p = fit_parser()
    # sanity checks
    assert 61 in p.cadence_list
    assert p.avg_cadence == 64
    assert p.max_cadence is None
    assert p.min_cadence is None

    # check min max values
    p._save_data_to_dataframe()
    p._set_min_max_values()
    assert p.max_cadence == 116.0
    assert p.min_cadence == 0.0
    assert p.max_speed == 3.57
    assert p.min_speed == 0.0
    assert p.max_temperature == 31.0
    assert p.min_temperature == 26.0
    assert p.max_altitude == 353.3
    assert p.min_altitude == 238.2
    assert p.max_heart_rate == 160.0
    assert p.min_heart_rate == 95.0
    with pytest.raises(AttributeError):
        assert p.max_timestamps == 0.0
    with pytest.raises(AttributeError):
        assert p.max_distance == 0.0
    with pytest.raises(AttributeError):
        assert p.max_coordinates == 0.0


def test_drop_rows_where_all_records_are_null(fit_parser):
    p = fit_parser()
    # null rows should already be dropped, can only verify that
    # there are no more rows will all null records present
    pd.testing.assert_frame_equal(p.dataframe, p.dataframe.dropna(how="all"))


def test_convert_list_of_nones_to_empty_list(fit_parser, monkeypatch):
    # mock away post processing in order to test before and after state
    def post_process(baz):
        return "foo"

    monkeypatch.setattr(FITParser, "_post_process_data", post_process)

    p = fit_parser("with_nones.fit")
    assert p.altitude_list[:3] == [None, None, None]
    p._save_data_to_dataframe()
    assert p.dataframe.altitude_list.isna().all()
    p._convert_list_of_nones_to_empty_list()
    assert p.altitude_list == []


def test_get_fastest_sections(fit_parser):
    p = fit_parser()

    # check that fastest sections dict is empty
    assert p.best_sections == []

    p.get_best_sections()

    assert p.best_sections != []

    sec1 = GenericBestSection(1000, 622, 712, 2.89, "fastest")
    sec2 = GenericBestSection(2000, 537, 814, 2.32, "fastest")
    sec3 = GenericBestSection(3000, 428, 937, 2.13, "fastest")
    sec4 = GenericBestSection(5000, 76, 1167, 1.84, "fastest")
    sec5 = GenericBestSection(100, 555, 580, 13.05, "climb")
    sec6 = GenericBestSection(200, 535, 578, 9.73, "climb")
    sec7 = GenericBestSection(500, 469, 578, 6.75, "climb")
    sec8 = GenericBestSection(1_000, 339, 580, 5.78, "climb")
    sec9 = GenericBestSection(2_000, 50, 584, 5.0, "climb")

    assert p.best_sections == [sec1, sec2, sec3, sec4, sec5, sec6, sec7, sec8, sec9]


def test__set_avg_values(fit_parser, monkeypatch):
    # mock away post processing in order to test before and after state
    def post_process(baz):
        return "foo"

    monkeypatch.setattr(FITParser, "_post_process_data", post_process)

    p = fit_parser()

    # in test fit file average speed is present
    assert p.avg_speed == 1.845
    assert p.avg_heart_rate == 130
    assert p.avg_cadence == 64
    assert p.avg_temperature == 27

    # however, remove avg attributes to test it will be set during post processing
    p.avg_speed = None
    p.avg_heart_rate = None
    p.avg_cadence = None
    p.avg_temperature = None

    assert p.avg_speed is None
    assert p.avg_heart_rate is None
    assert p.avg_cadence is None
    assert p.avg_temperature is None

    assert not hasattr(p, "dataframe")

    p._save_data_to_dataframe()
    assert hasattr(p, "dataframe")

    p._set_avg_values()

    # now avg and min max values should be present
    assert p.avg_speed == 1.71
    assert p.avg_heart_rate == 129.72
    assert p.avg_cadence == 63.96
    assert p.avg_temperature == 26.91
