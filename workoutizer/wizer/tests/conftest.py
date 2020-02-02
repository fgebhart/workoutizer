import os
import pytest

from wizer.file_helper.gpx_exporter import gpx_header
from wizer.file_helper.fit import FITParser


@pytest.fixture(scope="module")
def fit_parser():
    test_file_path = os.path.join(os.path.dirname(__file__), "data/example.fit")

    def _pass_path(path=test_file_path):
        return FITParser(path_to_file=path)

    return _pass_path


@pytest.fixture(scope='session')
def trace_coordinates():
    return [[8.476648433133962, 49.48468884453178], [8.476595375686886, 49.48457719758154],
            [8.47659705206752, 49.48453864082695], [8.47659654915333, 49.48450796306134]]


# @pytest.fixture(scope='session')
# def trace_altitude():
#     return [365.9, 365.9, 365.9, 366.0]
#
#
# @pytest.fixture(scope='session')
# def trace_heart_rate():
#     return [96, 96, 93, 99]


@pytest.fixture(scope='session')
def gpx_string():
    return f"""{gpx_header}
    <metadata>
        <time>2019-12-03T18:53:44Z</time>
    </metadata>
    <trk>
        <name>test</name>
        <trkseg>
            <trkpt lat="49.48468884453178" lon="8.476648433133962"></trkpt>
            <trkpt lat="49.48457719758154" lon="8.476595375686886"></trkpt>
            <trkpt lat="49.48453864082695" lon="8.47659705206752"></trkpt>
            <trkpt lat="49.48450796306134" lon="8.47659654915333"></trkpt>
            
        </trkseg>
    </trk>
</gpx>
"""
