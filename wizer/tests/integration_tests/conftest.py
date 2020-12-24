import pytest

from wizer import models


@pytest.fixture
def tracks_in_tmpdir(tmpdir):
    target_dir = tmpdir.mkdir("tracks")
    settings = models.get_settings()
    settings.path_to_trace_dir = target_dir
    settings.save()
