import datetime
from pathlib import Path

import pytest

from wkz.file_helper.parser import Parser
from wkz.file_importer import (
    _all_files_in_db_already,
    _check_and_parse_file,
    _convert_list_attributes_to_json,
    _get_all_files,
    _map_sport_name,
    _parse_single_file,
    sport_naming_map,
)
from wkz.tools.utils import calc_md5


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


def test__all_files_in_db_already(demo_data_dir):
    all_files = list(Path(demo_data_dir).iterdir())
    assert _all_files_in_db_already(all_files, []) is False

    # get all md5sums of existing files
    md5sums_from_db = []
    for trace in all_files:
        md5sums_from_db.append(calc_md5(trace))

    assert _all_files_in_db_already(all_files, md5sums_from_db) is True

    # remove only one md5sum and verify that result is False
    fewer_md5sums = md5sums_from_db[:-1]
    assert _all_files_in_db_already(all_files, fewer_md5sums) is False

    # remove one file (thus db all md5sums of existing files plus one) and verify result is True
    fewer_files = all_files[:-1]
    assert _all_files_in_db_already(fewer_files, md5sums_from_db) is True


@pytest.mark.parametrize("reimporting", (False, True))
def test__check_and_parse_file(demo_data_dir, reimporting):
    trace = Path(demo_data_dir) / "2019-09-18-16-02-35.fit"

    # file md5sum is not in db
    md5sums_from_db = []
    md5sum, path_to_file, parsed_file = _check_and_parse_file(trace, demo_data_dir, md5sums_from_db, reimporting)
    assert isinstance(md5sum, str)
    assert isinstance(path_to_file, Path)
    assert isinstance(parsed_file, Parser)

    if not reimporting:
        # file md5sum is in db
        md5sums_from_db = [calc_md5(trace)]
        md5sum, path_to_file, parsed_file = _check_and_parse_file(trace, demo_data_dir, md5sums_from_db, reimporting)
        assert isinstance(md5sum, str)
        assert isinstance(path_to_file, Path)
        assert parsed_file is None
