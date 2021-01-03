import os
import datetime

from gpxpy.gpxfield import SimpleTZ
from wizer.best_sections.fastest import FastestSection


def test__parse_metadata(gpx_parser):
    parser = gpx_parser()
    assert parser.file_name == "example.gpx"


def test__get_sport_duration_distance(gpx_parser):
    parser = gpx_parser()
    assert parser.sport == "running"
    assert parser.duration == datetime.timedelta(seconds=1502)
    assert parser.distance == 4.3
    assert parser.date == datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z"))


def test_get_date_from_metadata(gpx_parser, test_data_dir):
    test_file_path = os.path.join(test_data_dir, "garmin_example.gpx")
    parser = gpx_parser(path=test_file_path)
    assert parser.date == datetime.datetime(2019, 12, 16, 8, 58, 30, tzinfo=SimpleTZ("Z"))


def test_get_sport_from_type(gpx_parser, test_data_dir):
    test_file_path = os.path.join(test_data_dir, "garmin_example.gpx")
    parser = gpx_parser(path=test_file_path)
    assert parser.sport == "running"


def test__parse_coordinates(gpx_parser):
    parser = gpx_parser()
    assert parser.longitude_list[0] == 8.687453
    assert parser.latitude_list[0] == 49.405446
    assert parser.altitude_list[0] == 128.94


def test_parse_timestamps(gpx_parser):
    parser = gpx_parser()
    assert 1562951136.0 in parser.timestamps_list


def test_get_fastest_sections(gpx_parser):
    p = gpx_parser()

    # check that fastest sections dict is empty
    assert p.best_sections == []

    p.get_fastest_sections()

    assert p.best_sections != []

    sec1 = FastestSection(1, 54, 103, 3.14)
    sec2 = FastestSection(2, 54, 167, 3.07)
    sec3 = FastestSection(3, 1, 161, 2.98)

    assert p.best_sections == [sec1, sec2, sec3]
