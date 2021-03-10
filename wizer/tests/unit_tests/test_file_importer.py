from wizer.file_importer import (
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
