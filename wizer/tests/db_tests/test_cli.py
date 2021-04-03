import os
import subprocess

from django.core.management import execute_from_command_line
import pytest

from wizer import models
from workoutizer import cli
from workoutizer import __version__
from workoutizer import settings as django_settings


def test_cli_version():
    output = subprocess.check_output(["wkz", "--version"]).decode("utf-8")
    assert output == f"{__version__}\n"


def test_cli__init(db, tracks_in_tmpdir):
    cli._init(import_demo_activities=False)
    assert os.path.isdir(django_settings.WORKOUTIZER_DIR)
    assert len(models.Sport.objects.all()) == 0
    assert len(models.Activity.objects.all()) == 0
    assert len(models.Settings.objects.all()) == 1

    cli._init(import_demo_activities=True)
    assert os.path.isdir(django_settings.WORKOUTIZER_DIR)
    assert len(models.Sport.objects.all()) == 5
    assert len(models.Settings.objects.all()) == 1
    assert len(models.Activity.objects.all()) > 1


def test_cli__check__demo_data(db, tracks_in_tmpdir):
    # initialized wkz with demo data and then run check
    cli._init(import_demo_activities=True)
    cli._check()


def test_cli__check__no_demo_data(db, tracks_in_tmpdir):
    # initialized wkz without demo data and then run check
    cli._init(import_demo_activities=False)
    cli._check()


def test_cli__check__not_initialized(db, tracks_in_tmpdir):
    # if wkz is not initialized expect to raise error - ensure to start with no preexisting db
    execute_from_command_line(["manage.py", "flush", "--noinput"])
    with pytest.raises(cli.NotInitializedError, match="ERROR: Make sure to execute 'wkz init' first"):
        cli._check()


def test_cli__reimport(db, import_one_activity):
    import_one_activity("cycling_bad_schandau.fit")

    assert models.Activity.objects.count() == 1
    assert models.Settings.objects.count() == 1
    activity = models.Activity.objects.get()
    orig_distance = activity.distance
    activity.distance = 77_777.77
    activity.save()
    assert activity.distance != orig_distance

    cli._reimport()

    activity = models.Activity.objects.get()
    assert activity.distance == orig_distance
