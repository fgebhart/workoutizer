import pytest
from django.core.management import call_command


@pytest.fixture
def flush_db():
    call_command("flush", verbosity=0, interactive=False)
