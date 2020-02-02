from wizer.file_helper.gpx_exporter import _build_gpx


def test__build_gpx(trace_coordinates, gpx_string):
    assert type(_build_gpx(time='2019-12-03T18:53:44Z', file_name='test', coordinates=trace_coordinates)) == str
    assert _build_gpx(
        time='2019-12-03T18:53:44Z',
        file_name='test',
        coordinates=trace_coordinates).startswith('<?xml') is True
    assert _build_gpx(
        time='2019-12-03T18:53:44Z',
        file_name='test',
        coordinates=trace_coordinates) == gpx_string
