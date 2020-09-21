import os
import pytest

from wizer.file_helper.gpx_exporter import gpx_header
from wizer.file_helper.fit_parser import FITParser
from wizer.file_helper.gpx_parser import GPXParser


@pytest.fixture(scope="module")
def fit_parser():
    test_file_path = os.path.join(os.path.dirname(__file__), "../data/example.fit")

    def _pass_path(path=test_file_path):
        return FITParser(path_to_file=path)

    return _pass_path


@pytest.fixture(scope="module")
def gpx_parser():
    test_file_path = os.path.join(os.path.dirname(__file__), "../data/example.gpx")

    def _pass_path(path=test_file_path):
        return GPXParser(path_to_file=path)

    return _pass_path


@pytest.fixture(scope='session')
def trace_coordinates():
    return [[8.476648433133962, 49.48468884453178], [8.476595375686886, 49.48457719758154],
            [8.47659705206752, 49.48453864082695], [8.47659654915333, 49.48450796306134]]


@pytest.fixture(scope='session')
def trace_coordinates_with_elevation():
    return [[8.476648433133962, 49.48468884453178, 200], [8.476595375686886, 49.48457719758154, 201],
            [8.47659705206752, 49.48453864082695, 202], [8.47659654915333, 49.48450796306134, 203]]


@pytest.fixture(scope='session')
def gpx_string():
    return f"""{gpx_header}
    <metadata>
        <time>2019-07-12T00:00:00Z</time>
        <link href="https://github.com/fgebhart/workoutizer">
            <text>Workoutizer</text>
        </link>
    </metadata>
    <trk>
        <name>test</name>
            <type>Running</type>
        <trkseg>
            <trkpt lat="49.48468884453178" lon="8.476648433133962">
                <time>2019-07-12T12:00:00Z</time>
            </trkpt>
            <trkpt lat="49.48457719758154" lon="8.476595375686886">
                <time>2019-07-12T12:01:00Z</time>
            </trkpt>
            <trkpt lat="49.48453864082695" lon="8.47659705206752">
                <time>2019-07-12T12:02:00Z</time>
            </trkpt>
            <trkpt lat="49.48450796306134" lon="8.47659654915333">
                <time>2019-07-12T12:03:00Z</time>
            </trkpt>
            
        </trkseg>
    </trk>
</gpx>
"""


@pytest.fixture(scope='session')
def gpx_string_with_elevation():
    return f"""{gpx_header}
    <metadata>
        <time>2019-07-12T00:00:00Z</time>
        <link href="https://github.com/fgebhart/workoutizer">
            <text>Workoutizer</text>
        </link>
    </metadata>
    <trk>
        <name>test</name>
            <type>Running</type>
        <trkseg>
            <trkpt lat="49.48468884453178" lon="8.476648433133962">
                <time>2019-07-12T12:00:00Z</time>
                <ele>200</ele>
            </trkpt>
            <trkpt lat="49.48457719758154" lon="8.476595375686886">
                <time>2019-07-12T12:01:00Z</time>
                <ele>201</ele>
            </trkpt>
            <trkpt lat="49.48453864082695" lon="8.47659705206752">
                <time>2019-07-12T12:02:00Z</time>
                <ele>202</ele>
            </trkpt>
            <trkpt lat="49.48450796306134" lon="8.47659654915333">
                <time>2019-07-12T12:03:00Z</time>
                <ele>203</ele>
            </trkpt>
            
        </trkseg>
    </trk>
</gpx>
"""
