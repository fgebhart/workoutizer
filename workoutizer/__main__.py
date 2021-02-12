import os
import subprocess
import sys

import click
import requests
import luddite
from django.core.management import execute_from_command_line
from django.db.utils import OperationalError

from workoutizer.settings import WORKOUTIZER_DIR, WORKOUTIZER_DB_PATH, TRACKS_DIR
from workoutizer import __version__
from wizer.tools.utils import get_local_ip_address


os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"


@click.group()
def cli():
    pass


@click.command(
    help="Mandatory command to initialize workoutizer. This fetches the static files, creates the database, "
    "applies the required migrations and inserts the demo activities."
)
def init():
    _init()


@click.argument("url", default="")
@click.command(
    help="Run workoutizer. Passing the local ip address and port is optionally. In case of no ip address "
    "being passed, it will be determined automatically. Usage, e.g.: 'wkz run 0.0.0.0:8000'."
)
def run(url):
    _check()
    if not url:
        if os.getenv("WKZ_ENV") == "devel":
            url = "127.0.0.1:8000"
        else:
            url = f"{get_local_ip_address()}:8000"
    execute_from_command_line(["manage.py", "runserver", url])


@click.argument("cmd", nargs=1)
@click.command(
    help="Pass commands to django's manage.py. Convenience function to access all django commands which are "
    "not yet covered with the given set of workoutizer commands. Usage, e.g.: "
    "wkz manage 'runserver 0.0.0.0:8000 --noreload'."
)
def manage(cmd):
    execute_from_command_line(["manage.py"] + cmd.split(" "))


@click.command(help="Show the version of currently installed workoutizer.")
def version():
    click.echo(_version())


@click.command(help="Check for a newer version and install if there is any.")
def upgrade():
    _upgrade()


@click.command(help="Stop a running workoutizer instance.")
def stop():
    _stop()


@click.command(help="Check if workoutizer was properly installed")
def check():
    _check()


@click.command(help="Reimport all activities to update the given data.")
def reimport():
    _reimport()


cli.add_command(upgrade)
cli.add_command(stop)
cli.add_command(version)
cli.add_command(init)
cli.add_command(run)
cli.add_command(manage)
cli.add_command(check)
cli.add_command(reimport)


def _version():
    return __version__


def _upgrade():

    latest_version = luddite.get_version_pypi("workoutizer")
    from workoutizer import __version__ as current_version

    if latest_version == current_version:
        click.echo(f"No update available. You are running the latest version: {latest_version}")
    else:
        click.echo(f"found newer version: {latest_version}, you have {current_version} installed")
        _pip_install("workoutizer", upgrade=True)
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
        execute_from_command_line(["manage.py", "migrate"])
        execute_from_command_line(["manage.py", "check"])
        click.echo(f"Successfully upgraded from {current_version} to {latest_version}")


def _build_home(answer: str):
    if os.path.isdir(WORKOUTIZER_DIR):
        if os.path.isfile(WORKOUTIZER_DB_PATH):
            click.echo(f"Found existing workoutizer database at: {WORKOUTIZER_DB_PATH}\n")
            if not answer:
                answer = input(
                    "Workoutizer could try to use the existing database instead of creating a new one.\n"
                    "Note that this could lead to faulty behaviour because of mismatching applied\n"
                    "migrations on this database.\n\n"
                    "Do you want to use the existing database instead of creating a new one? \n"
                    "   - Enter 'n' to delete the found database and create a new one. \n"
                    "   - Enter 'y' to keep and use the found database. \n"
                    "Enter [Y/n] "
                )
            if answer.lower() == "n":
                click.echo(f"removed database at {WORKOUTIZER_DB_PATH}")
                os.remove(WORKOUTIZER_DB_PATH)
            else:
                click.echo(f"keeping existing database at {WORKOUTIZER_DB_PATH}")
                return
        _make_tracks_dir(TRACKS_DIR)
    else:
        os.mkdir(WORKOUTIZER_DIR)
        _make_tracks_dir(TRACKS_DIR)


def _init(answer: str = ""):
    _build_home(answer=answer)
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(["manage.py", "check"])

    # import demo activities
    from wizer import models
    from wizer.file_importer import import_activity_files, prepare_import_of_demo_activities

    prepare_import_of_demo_activities(models)
    import_activity_files(models, importing_demo_data=True)
    click.echo(f"Database and track files are stored in: {WORKOUTIZER_DIR}")


def _make_tracks_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def _pip_install(package, upgrade: bool = False):
    if upgrade:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade"])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def _stop():
    host = get_local_ip_address()
    click.echo(f"trying to stop workoutizer at {host}")
    url = f"http://{host}:8000/stop/"
    try:
        requests.post(url)
        click.echo("Stopped.")
    except requests.exceptions.ConnectionError:
        click.echo("Workoutizer is not running.")


class NotInitializedError(Exception):
    pass


def _check():
    msg = "Make sure to execute 'wkz init' first"
    try:
        execute_from_command_line(["manage.py", "check"])

        # second ensure that some activity data was imported
        from wizer import models

        if len(models.Settings.objects.all()) != 1:
            raise NotInitializedError(msg)

        if len(models.Activity.objects.all()) == 0:
            raise NotInitializedError(msg)
    except OperationalError:
        raise NotInitializedError(msg)


def _reimport():
    _check()

    from wizer import models
    from wizer.file_importer import reimport_activity_files

    reimport_activity_files(models)


if __name__ == "__main__":
    cli()
