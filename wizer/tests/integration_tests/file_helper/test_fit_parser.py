import os
import datetime

import pytz
import pytest
from django.conf import settings

from wizer.file_helper.fit_parser import LapData


tz = pytz.timezone(settings.TIME_ZONE)


def test__parse_metadata(fit_parser):
    p = fit_parser()
    assert p.file_name == 'example.fit'


def test__parse_records(fit_parser):
    p = fit_parser()
    # test single value attributes
    assert p.sport == 'running'
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
    assert len(p.heart_rate_list) == 4442
    assert len(p.altitude_list) == 4442
    assert len(p.latitude_list) == 4442
    assert len(p.longitude_list) == 4442
    assert len(p.distance_list) == 4442
    assert len(p.cadence_list) == 4442
    assert len(p.temperature_list) == 4442
    assert len(p.speed_list) == 4442
    assert len(p.timestamps_list) == 4442
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
        trigger='distance',
        speed=2.15,
    )


def test_get_min_max_values(fit_parser):
    p = fit_parser()
    # sanity checks
    assert 61 in p.cadence_list
    assert p.avg_cadence == 64
    assert p.max_cadence is None
    assert p.min_cadence is None

    # check min max values
    p.set_min_max_values()
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
        assert p.max_timestamps == 0.
    with pytest.raises(AttributeError):
        assert p.max_distance == 0.
    with pytest.raises(AttributeError):
        assert p.max_coordinates == 0.


def test_convert_list_attributes_to_json(fit_parser):
    p = fit_parser()
    assert type(p.timestamps_list) == list
    assert type(p.latitude_list) == list
    assert type(p.longitude_list) == list
    p.convert_list_attributes_to_json()
    assert type(p.timestamps_list) == str
    assert type(p.latitude_list) == str
    assert type(p.longitude_list) == str


def test_convert_list_of_nones_to_empty_list(fit_parser):
    p = fit_parser(path=os.path.join(os.path.dirname(__file__), "../data/with_nones.fit"))
    assert p.altitude_list[:3] == [None, None, None]
    p.convert_list_of_nones_to_empty_list()
    assert p.altitude_list == []


def test_parse_fit_record_wise(fit_parser):
    p = fit_parser()
