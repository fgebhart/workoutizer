import os
import pytest

from wkz.file_helper.gpx_exporter import gpx_header
from wkz.file_helper.fit_parser import FITParser
from wkz.file_helper.gpx_parser import GPXParser


@pytest.fixture
def fit_parser(test_data_dir, demo_data_dir):
    test_file_path = "example.fit"

    def _pass_path(path=test_file_path):
        file_in_test_data_dir = os.path.join(test_data_dir, path)
        file_in_demo_data_dir = os.path.join(demo_data_dir, path)
        if os.path.isfile(file_in_test_data_dir):
            return FITParser(path_to_file=file_in_test_data_dir)
        elif os.path.isfile(file_in_demo_data_dir):
            return FITParser(path_to_file=file_in_demo_data_dir)
        else:
            raise FileNotFoundError(f"file {path} neither found in {test_data_dir} nor in {demo_data_dir}")

    return _pass_path


@pytest.fixture
def gpx_parser(test_data_dir):
    test_file_path = os.path.join(test_data_dir, "example.gpx")

    def _pass_path(path=test_file_path):
        return GPXParser(path_to_file=path)

    return _pass_path


@pytest.fixture
def trace_coordinates():
    return [
        [8.476648433133962, 49.48468884453178],
        [8.476595375686886, 49.48457719758154],
        [8.47659705206752, 49.48453864082695],
        [8.47659654915333, 49.48450796306134],
    ]


@pytest.fixture
def trace_coordinates_with_elevation():
    return [
        [8.476648433133962, 49.48468884453178, 200],
        [8.476595375686886, 49.48457719758154, 201],
        [8.47659705206752, 49.48453864082695, 202],
        [8.47659654915333, 49.48450796306134, 203],
    ]


@pytest.fixture
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


@pytest.fixture
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
