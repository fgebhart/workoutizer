import os
import datetime

from gpxpy.gpxfield import SimpleTZ


def test__parse_metadata(gpx_parser):
    parser = gpx_parser()
    assert parser.name == 'example'


def test__get_sport_duration_distance(gpx_parser):
    parser = gpx_parser()
    assert parser.sport == 'running'
    assert parser.duration == datetime.timedelta(seconds=1502)
    assert parser.distance == 4.4
    assert parser.date == datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z"))


def test_get_date_from_metadata(gpx_parser):
    test_file_path = os.path.join(os.path.dirname(__file__), "data/garmin_example.gpx")
    parser = gpx_parser(path=test_file_path)
    assert parser.date == datetime.datetime(2019, 12, 16, 8, 58, 30, tzinfo=SimpleTZ("Z"))


def test__parse_coordinates(gpx_parser):
    parser = gpx_parser()
    assert parser.coordinates[0] == [8.687453, 49.405446]
    assert parser.altitude[0] == 128.94
