import datetime
from pathlib import Path

from wkz.file_helper.parser import Parser
from wkz.file_importer import (
    _parse_single_file,
    _map_sport_name,
    sport_naming_map,
    _convert_list_attributes_to_json,
    _get_all_files,
)


def test_map_sport_name():
    assert _map_sport_name("running", sport_naming_map) == "Jogging"
    assert _map_sport_name("Running", sport_naming_map) == "Jogging"
    assert _map_sport_name("swim", sport_naming_map) == "Swimming"
    assert _map_sport_name("SUP", sport_naming_map) == "unknown"


def test_convert_list_attributes_to_json(fit_parser):
    parser = fit_parser()
    assert type(parser.timestamps_list) == list
    assert type(parser.latitude_list) == list
    assert type(parser.longitude_list) == list
    parser = _convert_list_attributes_to_json(parser)
    assert type(parser.timestamps_list) == str
    assert type(parser.latitude_list) == str
    assert type(parser.longitude_list) == str


def test_get_all_files(tmpdir):
    gpx = tmpdir.mkdir("gpx").join("test.gpx")
    fit = tmpdir.mkdir("fit").join("test.fit")
    invalid = tmpdir.mkdir("txt").join("test.txt")
    for file in [gpx, fit, invalid]:
        file.write("some-content")
    assert len(_get_all_files(tmpdir)) == 2


def test__parse_single_file(demo_data_dir, fit_file):
    path = Path(demo_data_dir) / fit_file
    payload = _parse_single_file(path, demo_data_dir, "foo")
    assert isinstance(payload, Parser)

    # check core values which should have been changed
    assert payload.path_to_file == str(path)
    assert payload.file_name is not None
    assert payload.date is not None
    assert payload.md5sum == "foo"
    assert payload.sport is not None
    assert payload.duration != datetime.timedelta(minutes=0)
