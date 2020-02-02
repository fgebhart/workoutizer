import datetime

from gpxpy.gpxfield import SimpleTZ

from wizer.file_helper.gpx_exporter import _build_gpx, _fill_list_of_timestamps


def test__build_gpx(trace_coordinates, gpx_string):
    list_of_timestamps = _fill_list_of_timestamps(
        start=datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z")),
        duration=datetime.timedelta(minutes=4),
        length=len(trace_coordinates))
    assert _build_gpx(
        time=datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z")),
        file_name='test',
        coordinates=trace_coordinates,
        timestamps=list_of_timestamps,
    ) == gpx_string


def test__fill_list_of_timestamps():
    length = 3
    assert len(_fill_list_of_timestamps(
        start=datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z")),
        duration=datetime.timedelta(minutes=30),
        length=length,
    )) == length
    assert _fill_list_of_timestamps(
        start=datetime.datetime(2019, 7, 12, 17, 5, 36, tzinfo=SimpleTZ("Z")),
        duration=datetime.timedelta(minutes=30),
        length=length,
    ) == ['2019-07-12T17:05:36Z', '2019-07-12T17:15:36Z', '2019-07-12T17:25:36Z']
