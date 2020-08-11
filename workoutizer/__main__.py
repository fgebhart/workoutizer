import os
import argparse
import subprocess
import socket
import sys

import click
from django.core.management import execute_from_command_line

from workoutizer.settings import WORKOUTIZER_DIR, WORKOUTIZER_DB_PATH, TRACKS_DIR
from workoutizer import __version__

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SETUP_DIR = os.path.join(BASE_DIR, 'setup')
os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"

example_rpi_cmd = "wkz --setup_rpi vendor_id=091e product_id=4b48"
url_help = 'specify ip address and port pair, like: address:port'


@click.group()
def cli():
    pass


@click.command(help='Mandatory command to initialize workoutizer. This fetches the static files, creates the database '
                    'and applies the required migrations.')
def init():
    _build_home()
    execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(["manage.py", "check"])
    click.echo(f"database and track files are stored in: {WORKOUTIZER_DIR}")


@click.option('--ip', default="", help=url_help)
@click.option('--product_id', help="product ip of your device", required=True)
@click.option('--vendor_id', help="vendor ip of your device", required=True)
@click.command(help='Configure Raspberry Pi to auto mount devices. Passing vendor and product id is required. Passing '
                    f'the local ip address and port is optionally. E.g.: {example_rpi_cmd}')
def setup_rpi(ip, vendor_id, product_id):
    if not ip:
        ip = _get_local_ip_address()
    answer = input(f"Are you sure you want to setup your Raspberry Pi?\n\n"
                   f"This will copy the required udev rule and systemd service file\n"
                   f"to your system to enable automated mounting of your device.\n"
                   f"This might take a while...\n\n"
                   f"Start setup? [Y/n] ")
    if answer.lower() == 'y':
        click.echo(f"installing ansible...")
        _pip_install('ansible==2.9.10')
        click.echo(f"starting setup using ansible...")
        _setup_rpi(
            vendor_id=vendor_id,
            product_id=product_id,
            ip_port=f"{ip}:8000"
        )
        _run_ansible(playbook='install_packages.yml')
        click.echo(f"Successfully configured to automatically mount your device when plugged in. Note: These changes "
                   f"require a system restart to take effect.")
    else:
        click.echo(f"Aborted.")


@click.argument('url', default="")
@click.command(help="Run workoutizer. Passing the local ip address and port is optionally. In case of no ip address "
                    "being passed, it will be determined automatically. Usage, e.g.: 'wkz run 0.0.0.0:8000'.")
def run(url):
    if not url:
        url = f"{_get_local_ip_address()}:8000"
    execute_from_command_line(["manage.py", "runserver", url])


@click.argument('url', default="")
@click.command(help='Configure workoutizer to run as systemd service. Passing the local ip address and port is '
                    'optionally. In case of no ip address being passed, it will be determined automatically.')
def wkz_as_service(url):
    _pip_install('ansible==2.9.10')
    _wkz_as_service(url=url)


@click.argument('cmd', nargs=1)
@click.command(help="Pass commands to django's manage.py. Convenience function to access all django commands which are "
                    "not yet covered with the given set of workoutizer commands. Usage, e.g.: "
                    "wkz manage 'runserver 0.0.0.0:8000 --noreload'.")
def manage(cmd):
    execute_from_command_line(["manage.py"] + cmd.split(' '))


@click.command(help='Show the version of currently installed workoutizer.')
def version():
    click.echo(__version__)


@click.command(help='Check for a newer version and install if there is any.')
def upgrade():
    _upgrade()


cli.add_command(upgrade)
cli.add_command(version)
cli.add_command(init)
cli.add_command(setup_rpi)
cli.add_command(run)
cli.add_command(manage)
cli.add_command(wkz_as_service)


def _upgrade():
    latest_version = _get_latest_version_of("workoutizer")
    from workoutizer import __version__ as current_version
    if latest_version:
        click.echo(f"found newer version: {latest_version}, you have {current_version} installed")
        _pip_install('workoutizer', upgrade=True)
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
        execute_from_command_line(["manage.py", "migrate"])
        execute_from_command_line(["manage.py", "check"])
        click.echo(f"Successfully upgraded from {current_version} to {latest_version}")
    else:
        click.echo(f"No update available. You are running the latest version: {current_version}")


def _get_latest_version_of(package: str):
    outdated = str(
        subprocess.check_output([sys.executable, "-m", "pip", "list", '--outdated', '--disable-pip-version-check']))
    if package in outdated:
        output = str(subprocess.check_output([sys.executable, "-m", "pip", "search", package]))
        latest_version = output[output.find('LATEST'):].split('\\n')[0].split(' ')[-1]
        return latest_version
    else:
        return False


def _setup_rpi(vendor_id: str, product_id: str, ip_port: str = None):
    if not ip_port:
        ip_port = f"{_get_local_ip_address()}:8000"
    result = _run_ansible(
        playbook='setup_on_rpi.yml',
        variables={
            'vendor_id': vendor_id,
            'product_id': product_id,
            'address_plus_port': ip_port,
        }
    )
    if result == 0:
        pass
    else:
        click.echo(f"ERROR: Could not configure Raspberry Pi, see above errors.")
        quit()
    return result


def _wkz_as_service(url: str):
    click.echo(f"configuring workoutizer to run as system service")
    if not url:
        url = f"{_get_local_ip_address()}:8000"
    env_binaries = sys.executable
    wkz_executable = env_binaries[:env_binaries.find('python')] + "wkz"
    result = _run_ansible(
        playbook='wkz_as_service.yml',
        variables={
            'address_plus_port': url,
            'wkz_executable': wkz_executable,
        }
    )
    if result == 0:
        click.echo(f"Successfully configured workoutizer as systemd service. Run it with: systemctl start wkz.service")
    else:
        click.echo(f"ERROR: Could not configure workoutizer as systemd service, see above errors.")
    return result


def _get_local_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def _build_home():
    if os.path.isdir(WORKOUTIZER_DIR):
        if os.path.isfile(WORKOUTIZER_DB_PATH):
            click.echo(f"Found existing workoutizer database at: {WORKOUTIZER_DB_PATH}\n")
            answer = input(f"Workoutizer could try to use the existing database instead of creating a new one.\n"
                           f"Note that this could lead to faulty behaviour because of mismatching applied\n"
                           f"migrations on this database.\n\n"
                           f"Do you want to use the existing database instead of creating a new one? [Y/n] ")
            if answer.lower() == 'y':
                click.echo(f"keeping existing database at {WORKOUTIZER_DB_PATH}")
                return
            else:
                click.echo(f"removed database at {WORKOUTIZER_DB_PATH}")
                os.remove(WORKOUTIZER_DB_PATH)
        _make_tracks_dir(TRACKS_DIR)
    else:
        os.mkdir(WORKOUTIZER_DIR)
        _make_tracks_dir(TRACKS_DIR)


def _make_tracks_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


class ParseDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        d = {}
        if values:
            for item in values:
                split_items = item.split("=", 1)
                key = split_items[0].strip()  # we remove blanks around keys, as is logical
                value = split_items[1]
                d[key] = value

        setattr(namespace, self.dest, d)


def _pip_install(package, upgrade: bool = False):
    if upgrade:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, '--upgrade'])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def _run_ansible(playbook: str, variables: dict = None):
    if variables is None:
        variables = {}
    from ansible import context
    from ansible.cli import CLI
    from ansible.module_utils.common.collections import ImmutableDict
    from ansible.executor.playbook_executor import PlaybookExecutor
    from ansible.parsing.dataloader import DataLoader
    from ansible.inventory.manager import InventoryManager
    from ansible.vars.manager import VariableManager

    loader = DataLoader()
    context.CLIARGS = ImmutableDict(
        tags={}, listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None,
        forks=100, remote_user='xxx', private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
        sftp_extra_args=None, scp_extra_args=None, become=True, become_method='sudo', become_user='root',
        verbosity=True, check=False, start_at_task=None
    )
    inventory = InventoryManager(loader=loader, sources=())
    variable_manager = VariableManager(loader=loader, inventory=inventory, version_info=CLI.version_info(gitinfo=False))
    variable_manager._extra_vars = variables
    pbex = PlaybookExecutor(playbooks=[os.path.join(SETUP_DIR, 'ansible', playbook)], inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader, passwords={})
    return pbex.run()


if __name__ == '__main__':
    cli()
