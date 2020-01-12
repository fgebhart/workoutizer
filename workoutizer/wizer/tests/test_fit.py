import datetime


def test__parse_metadata(fit_parser):
    parser = fit_parser()
    assert parser.name == 'example'


def test__get_sport_duration_distance(fit_parser):
    parser = fit_parser()
    assert parser.sport == 'running'
    assert parser.duration == datetime.timedelta(seconds=3164)
    assert parser.distance == 5.84


def test__parse_coordinates(fit_parser):
    parser = fit_parser()
    assert parser.coordinates[0] == [8.694167453795673, 49.40601873211563]
    assert parser.altitude[0] == 248.7


def test_parse_heart_rate(fit_parser):
    parser = fit_parser()
    parser.parse_heart_rate()
    assert parser.heart_rate[:3] == [100, 99, 96]

