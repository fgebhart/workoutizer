import datetime


def test__parse_metadata(fit_parser):
    parser = fit_parser()
    assert parser.file_name == 'example.fit'


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
    assert p.altitude_list[0] == 248.7
    assert p.heart_rate_list[:3] == [100, 99, 96]
    assert p.avg_heart_rate == 130
    assert p.cadence_list[:3] == [61, 0, 0]
    assert p.avg_cadence == 64
    assert p.temperature_list[:3] == [31, 31, 31]
    assert p.avg_temperature == 27
    assert p.aerobic_training_effect == 2.7
    assert p.anaerobic_training_effect == 0.3
