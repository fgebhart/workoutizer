import pytest
from django.core.management import call_command

from wizer import models


@pytest.fixture
def tracks_in_tmpdir(tmpdir):
    target_dir = tmpdir.mkdir("tracks")
    settings = models.get_settings()
    settings.path_to_trace_dir = target_dir
    settings.save()


@pytest.fixture
def flush_db():
    call_command("flush", verbosity=0, interactive=False)
