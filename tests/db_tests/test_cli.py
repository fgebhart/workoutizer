import os

from click.testing import CliRunner
from django.core.management import execute_from_command_line

from wkz import models
from workoutizer import __version__, cli
from workoutizer import settings as django_settings
from workoutizer.cli import wkz


def test_cli_version():
    runner = CliRunner()
    output = runner.invoke(wkz, ["--version"])
    assert output.stdout == f"{__version__}\n"


def test_cli__init(tracks_in_tmpdir):
    runner = CliRunner()
    runner.invoke(wkz, ["init"])
    assert os.path.isdir(django_settings.WORKOUTIZER_DIR)
    assert len(models.Sport.objects.all()) == 0
    assert len(models.Activity.objects.all()) == 0
    assert len(models.Settings.objects.all()) == 1

    runner = CliRunner()
    runner.invoke(wkz, ["init", "--demo"])
    assert os.path.isdir(django_settings.WORKOUTIZER_DIR)
    assert len(models.Sport.objects.all()) == 4
    assert len(models.Settings.objects.all()) == 1
    assert len(models.Activity.objects.all()) > 1


def test_cli__check__demo_data(tracks_in_tmpdir):
    # initialized wkz with demo data and then run check
    runner = CliRunner()
    runner.invoke(wkz, ["init", "--demo"])
    runner.invoke(wkz, ["check"])


def test_cli__check__no_demo_data(db):
    # initialized wkz without demo data and then run check
    runner = CliRunner()
    runner.invoke(wkz, ["init"])
    runner.invoke(wkz, ["check"])


def test_cli__check__not_initialized(db):
    # if wkz is not initialized expect to raise error - ensure to start with no preexisting db
    execute_from_command_line(["manage.py", "flush", "--noinput"])
    runner = CliRunner()
    result = runner.invoke(wkz, ["check"])
    assert isinstance(result.exception, cli.NotInitializedError)


def test_cli__reimport(import_one_activity):
    import_one_activity("cycling_bad_schandau.fit")

    assert models.Activity.objects.count() == 1
    assert models.Settings.objects.count() == 1
    activity = models.Activity.objects.get()
    orig_distance = activity.distance
    activity.distance = 77_777.77
    activity.save()
    assert activity.distance != orig_distance

    runner = CliRunner()
    runner.invoke(wkz, ["reimport"])

    activity = models.Activity.objects.get()
    assert activity.distance == orig_distance


def test__check_for_update(monkeypatch):
    # mock pypi version to be lower than the current version
    pypi_version = "0.0.1"

    def mocked_get_version_pypi(pkg):
        return pypi_version

    monkeypatch.setattr(cli.luddite, "get_version_pypi", mocked_get_version_pypi)

    assert cli._check_for_update() is False
    runner = CliRunner()
    output = runner.invoke(wkz, ["check-for-update"])
    assert output.stdout == (
        f"Your installed version ({__version__}) seems to be greater than "
        f"the latest version on pypi ({pypi_version}).\n"
    )

    # mock pypi version to equal the current version
    pypi_version = __version__

    def mocked_get_version_pypi(pkg):
        return pypi_version

    monkeypatch.setattr(cli.luddite, "get_version_pypi", mocked_get_version_pypi)

    assert cli._check_for_update() is False
    runner = CliRunner()
    output = runner.invoke(wkz, ["check-for-update"])
    assert output.stdout == f"No update available. You are running the latest version: {__version__}\n"

    # mock pypi version to be larger than the current version
    pypi_version = "9999.9999.9999"

    def mocked_get_version_pypi(pkg):
        return pypi_version

    monkeypatch.setattr(cli.luddite, "get_version_pypi", mocked_get_version_pypi)

    assert cli._check_for_update() is True
    runner = CliRunner()
    output = runner.invoke(wkz, ["check-for-update"])
    assert output.stdout == f"Newer version available: {pypi_version}. You are running: {__version__}\n"
