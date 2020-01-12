import os
import pytest

from wizer.format.fit import FITParser


@pytest.fixture(scope="module")
def fit_parser():
    test_file_path = os.path.join(os.path.dirname(__file__), "data/example.fit")

    def _pass_path(path=test_file_path):
        return FITParser(path_to_file=path)
    return _pass_path
