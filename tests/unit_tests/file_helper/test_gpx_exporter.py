import datetime


from wkz.file_helper.gpx_exporter import _build_gpx, _fill_list_of_timestamps


def test__build_gpx(trace_coordinates, gpx_string):
    list_of_timestamps = _fill_list_of_timestamps(
        start=datetime.datetime(2019, 7, 12), duration=datetime.timedelta(minutes=4), length=len(trace_coordinates)
    )
    assert (
        _build_gpx(
            time=datetime.datetime(2019, 7, 12),
            file_name="test",
            coordinates=trace_coordinates,
            timestamps=list_of_timestamps,
            sport="Running",
        )
        == gpx_string
    )


def test__build_gpx_with_elevation(trace_coordinates_with_elevation, gpx_string_with_elevation):
    list_of_timestamps = _fill_list_of_timestamps(
        start=datetime.datetime(2019, 7, 12),
        duration=datetime.timedelta(minutes=4),
        length=len(trace_coordinates_with_elevation),
    )
    assert (
        _build_gpx(
            time=datetime.datetime(2019, 7, 12),
            file_name="test",
            coordinates=trace_coordinates_with_elevation,
            timestamps=list_of_timestamps,
            sport="Running",
        )
        == gpx_string_with_elevation
    )


def test__fill_list_of_timestamps():
    length = 3
    assert (
        len(
            _fill_list_of_timestamps(
                start=datetime.datetime(2019, 7, 12),
                duration=datetime.timedelta(minutes=30),
                length=length,
            )
        )
        == length
    )
    assert (
        _fill_list_of_timestamps(
            start=datetime.datetime(2019, 7, 12),
            duration=datetime.timedelta(minutes=30),
            length=length,
        )
        == ["2019-07-12T12:00:00Z", "2019-07-12T12:10:00Z", "2019-07-12T12:20:00Z"]
    )
