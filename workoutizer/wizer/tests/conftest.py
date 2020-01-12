import pytest

from wizer.format.fit import FITParser


@pytest.fixture(scope="module")
def fit_parser():
    def pass_path(path):
        return path
    return FITParser(path_to_file=pass_path)
