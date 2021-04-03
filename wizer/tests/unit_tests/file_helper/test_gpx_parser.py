import os
import datetime

from gpxpy.gpxfield import SimpleTZ
from wizer.best_sections.generic import GenericBestSection


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

    # check that fastest sections list is empty
    assert p.best_sections == []

    p.get_best_sections()

    assert p.best_sections != []

    sec1 = GenericBestSection(1000, 57, 118, 3.05, "fastest")
    sec2 = GenericBestSection(2000, 54, 171, 3.04, "fastest")
    sec3 = GenericBestSection(3000, 10, 173, 2.96, "fastest")
    sec4 = GenericBestSection(100, 115, 121, 17.98, "climb")
    sec5 = GenericBestSection(200, 8, 22, 13.55, "climb")
    sec6 = GenericBestSection(500, 62, 92, 11.95, "climb")
    sec7 = GenericBestSection(1_000, 175, 239, 10.62, "climb")
    sec8 = GenericBestSection(2_000, 111, 240, 9.64, "climb")

    assert p.best_sections == [sec1, sec2, sec3, sec4, sec5, sec6, sec7, sec8]
