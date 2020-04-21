import os
import datetime


def test__parse_metadata(fit_parser):
    p = fit_parser()
    assert p.file_name == 'example.fit'


def test__parse_records(fit_parser):
    p = fit_parser()
    assert p.sport == 'running'
    assert p.distance == 5.84
    assert p.duration == datetime.timedelta(seconds=3164)
    assert p.date == datetime.datetime(2019, 9, 14, 16, 15)
    assert p.calories == 432
    assert p.speed_list[:3] == [1.605, 1.577, 1.577]
    assert p.avg_speed == 1.845
    assert p.coordinates_list[0] == [8.694167453795673, 49.40601873211563]
    assert p.altitude_list[0] == 248.9
    assert p.heart_rate_list[:3] == [100, 99, 96]
    assert p.avg_heart_rate == 130
    assert p.cadence_list[:3] == [61, 0, 0]
    assert p.avg_cadence == 64
    assert p.temperature_list[:3] == [31, 31, 31]
    assert p.avg_temperature == 27
    assert p.aerobic_training_effect == 2.7
    assert p.anaerobic_training_effect == 0.3
    assert len(p.heart_rate_list) == 1202
    assert len(p.altitude_list) == 4157
    assert len(p.coordinates_list) == 4157
    assert len(p.coordinates_list) == len(p.altitude_list)
    assert len(p.cadence_list) == 1202
    assert len(p.temperature_list) == 1202
    assert len(p.speed_list) == 1201
    assert len(p.timestamps_list) == 1224


def test_get_min_max_values(fit_parser):
    p = fit_parser()
    assert p.cadence_list[:3] == [61, 0, 0]
    assert p.avg_cadence == 64
    assert p.max_cadence is None
    assert p.min_cadence is None
    p.set_min_max_values()
    assert p.max_cadence == 116.0
    assert p.min_cadence == 0.0


def test_convert_list_attributes_to_json(fit_parser):
    p = fit_parser()
    assert type(p.timestamps_list) == list
    assert type(p.coordinates_list) == list
    p.convert_list_attributes_to_json()
    assert type(p.timestamps_list) == str
    assert type(p.coordinates_list) == str


def test_convert_list_of_nones_to_empty_list(fit_parser):
    p = fit_parser(path=os.path.join(os.path.dirname(__file__), "../data/with_nones.fit"))
    assert p.altitude_list[:3] == [None, None, None]
    p.convert_list_of_nones_to_empty_list()
    assert p.altitude_list == []


