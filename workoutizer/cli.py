import os
import subprocess
import sys
from pathlib import Path

import click
import luddite
import requests
from django.core.management import execute_from_command_line
from django.db.utils import OperationalError

from wkz.tools.utils import get_local_ip_address
from workoutizer import __version__
from workoutizer.settings import TRACKS_DIR, WORKOUTIZER_DB_PATH, WORKOUTIZER_DIR

os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.option(
    "-v", "--version", help="prints the version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
@click.group()
def wkz():
    pass


@click.option("-d", "--demo", help="adds demo activity data", is_flag=True)
@click.command(
    help="Mandatory command to initialize workoutizer. This fetches the static files, creates the database, "
    "applies the required migrations and inserts the demo activities."
)
def init(demo: bool):
    _init(import_demo_activities=demo)


def _is_main_run():
    return os.environ.get("RUN_MAIN", None) != "true"


@click.argument("url", default="")
@click.command(
    help="Run workoutizer. Passing the local ip address and port is optionally. In case of no ip address "
    "being passed, it will be determined automatically. Usage, e.g.: 'wkz run 0.0.0.0:8000'."
)
def run(url):
    if not url:
        if os.getenv("WKZ_ENV") == "devel":
            url = "0.0.0.0:8000"
        else:
            url = f"{get_local_ip_address()}:8000"
    if _is_main_run():
        click.echo(f"using workoutizer home at {WORKOUTIZER_DIR}")
    with HueyManager():
        execute_from_command_line(["manage.py", "runserver", url, "--insecure"])


@click.argument("cmd", nargs=1)
@click.command(
    help="Pass commands to django's manage.py. Convenience function to access all django commands. Usage, e.g.: "
    "wkz manage 'runserver 0.0.0.0:8000 --noreload'"
)
def manage(cmd):
    execute_from_command_line(["manage.py"] + cmd.split(" "))


@click.command(help="Upgrade workoutizer to newer version, if there is any.")
def upgrade():
    _upgrade()


@click.command(help="Check if a new version is available.")
def check_for_update():
    _check_for_update()


@click.command(help="Stop a running workoutizer instance.")
def stop():
    _stop()


@click.command(help="Check if workoutizer was properly installed")
def check():
    _check()


@click.command(help="Reimport all activities to update the given data.")
def reimport():
    _reimport()


wkz.add_command(upgrade)
wkz.add_command(stop)
wkz.add_command(init)
wkz.add_command(run)
wkz.add_command(manage)
wkz.add_command(check)
wkz.add_command(check_for_update)
wkz.add_command(reimport)


def _upgrade():
    from workoutizer import __version__ as current_version

    if _check_for_update():
        click.echo("upgrading workoutizer...")
        new_version = _pip_install("workoutizer")
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
        execute_from_command_line(["manage.py", "migrate"])
        execute_from_command_line(["manage.py", "check"])

        click.echo(f"Successfully upgraded from {current_version} to {new_version}")


def _check_for_update() -> bool:
    pypi_version = luddite.get_version_pypi("workoutizer")
    from workoutizer import __version__ as current_version

    if pypi_version > current_version:
        click.echo(f"Newer version available: {pypi_version}. You are running: {current_version}")
        return True
    elif pypi_version == current_version:
        click.echo(f"No update available. You are running the latest version: {pypi_version}")
        return False
    else:  # current_version > pypi_version
        click.echo(
            f"Your installed version ({current_version}) seems to be greater "
            f"than the latest version on pypi ({pypi_version})."
        )
        return False


def _build_home() -> None:
    if Path(WORKOUTIZER_DIR).is_dir():
        if Path(TRACKS_DIR).is_dir():
            # both folders are already created - do nothing
            return
        else:
            Path(TRACKS_DIR).mkdir(exist_ok=True)
    else:
        Path(WORKOUTIZER_DIR).mkdir(exist_ok=True)
        Path(TRACKS_DIR).mkdir(exist_ok=True)


def _init(import_demo_activities: bool = False):
    _build_home()
    if Path(WORKOUTIZER_DB_PATH).is_file():
        execute_from_command_line(["manage.py", "check"])
        from wkz import models

        try:
            if models.Settings.objects.count() == 1:
                if models.Activity.objects.count() == 0 and import_demo_activities:
                    click.echo("Found initialized db, but with no demo activity, importing...")
                else:
                    click.echo(
                        f"Found initialized db at {WORKOUTIZER_DB_PATH}, maybe you want to run wkz \n"
                        "instead. If you really want to initialize wkz consider removing the existing db file. \n"
                        "Aborting."
                    )
                    return
        except OperationalError:
            pass  # means required tables are not set up - continuing with applying migrations
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    execute_from_command_line(["manage.py", "migrate"])
    from wkz import models

    # insert settings
    models.get_settings()
    _check()

    if import_demo_activities:
        # import demo activities
        from wkz.demo import prepare_import_of_demo_activities
        from wkz.file_importer import run_importer__dask

        prepare_import_of_demo_activities(models)
        run_importer__dask(models, importing_demo_data=True)
        click.echo(f"Database and track files are stored in: {WORKOUTIZER_DIR}")


def _pip_install(package: str) -> str:
    pypi_version = luddite.get_version_pypi("workoutizer")
    package = f"{package}=={pypi_version}"
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return pypi_version


def _stop():
    host = get_local_ip_address()
    click.echo(f"stopping workoutizer at {host}")
    url = f"http://{host}:8000/stop/"
    try:
        requests.post(url)
        click.echo("Stopped.")
    except requests.exceptions.ConnectionError:
        click.echo("Workoutizer is not running.")


class NotInitializedError(Exception):
    pass


def _check():
    try:
        execute_from_command_line(["manage.py", "check"])

        # ensure that at least settings are present
        from wkz import models

        if models.Settings.objects.count() != 1:
            raise NotInitializedError("ERROR: Make sure to execute 'wkz init' first")

    except OperationalError:
        raise NotInitializedError("ERROR: Make sure to execute 'wkz init' first")


def _reimport():
    _check()

    from wkz import models
    from wkz.file_importer import run_importer__dask

    run_importer__dask(models, reimporting=True)


class HueyManager:
    def __init__(self):
        self.process = None

    def __enter__(self):
        if _is_main_run():
            self.process = subprocess.Popen([sys.executable, "-m", "django", "run_huey"])
            return self.process

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.process:
            self.process.terminate()
