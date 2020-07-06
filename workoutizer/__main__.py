import os
import logging
import argparse
import subprocess
import sys
from typing import List
from logging.config import dictConfig

from django.core.management import execute_from_command_line

from workoutizer.logger import get_logging_for_wkz
from workoutizer.settings import WORKOUTIZER_DIR, WORKOUTIZER_DB_PATH, TRACKS_DIR

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SETUP_DIR = os.path.join(BASE_DIR, 'setup')

logging.config.dictConfig(get_logging_for_wkz())
log = logging.getLogger("wkz")

example_rpi_cmd = "wkz --setup_rpi vendor_id=091e product_id=4b48 address_plus_port=192.168.0.108:8000"


def cli():
    parser = argparse.ArgumentParser(description='Workoutizer - Workout Organizer')
    command_group = parser.add_mutually_exclusive_group()
    command_group.add_argument('run', help='runs the workoutizer application', nargs='?')
    command_group.add_argument('init', help='collects static files and migrates the db schema to a newer version',
                               nargs='?')
    parser.add_argument("-s", "--setup_rpi", metavar="KEY=VALUE", help="Setup raspberry pi. Provide product and vendor"
                                                                       "id like: \n" + example_rpi_cmd,
                        action=ParseDict, nargs=3)
    parser.add_argument("-m", "--manage", help="pass arguments to django's manage.py", nargs='+')
    parser.add_argument("-d", "--run_as_systemd", metavar="ip_port=ip:port",
                        help="configure workoutizer to run as systemd service", action=ParseDict, nargs=1)

    args = parser.parse_args()
    os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"
    if args.run == 'run':
        execute_from_command_line(["manage.py", "runserver"])
    elif args.run == 'init':
        _build_home()
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
        execute_from_command_line(["manage.py", "migrate"])
        execute_from_command_line(["manage.py", "check"])
    elif args.setup_rpi:
        _check_keys_exist(keys=['product_id', 'vendor_id', 'address_plus_port'], arguments=args.setup_rpi)
        answer = input(f"Are you sure you want to setup your Raspberry Pi?\n\n"
                       f"This will copy the required udev rule and systemd service file\n"
                       f"to your system to enable automated mounting of your device.\n\n"
                       f"Start setup? [Y/n] ")
        if answer.lower() == 'y':
            log.info(f"installing ansible...")
            _pip_install('ansible==2.9.10')
            log.info(f"starting setup using ansible...")
            _run_ansible(
                playbook='setup_on_rpi.yml',
                variables={
                    'vendor_id': args.setup_rpi['vendor_id'],
                    'product_id': args.setup_rpi['product_id'],
                    'address_plus_port': args.setup_rpi['address_plus_port'],
                }
            )
        else:
            log.info(f"Aborted.")
    elif args.manage:
        execute_from_command_line(["manage.py"] + args.manage)
    elif args.run_as_systemd:
        _check_keys_exist(keys=['ip_port'], arguments=args.run_as_systemd)
        _configure_to_run_as_systemd_service(
            address_plus_port=args.run_as_systemd['ip_port'],
            wkz_service_path='/etc/systemd/system/wkz.service',
        )
    else:
        parser.print_help()
        return 1

    return 0


def _configure_to_run_as_systemd_service(address_plus_port: str, wkz_service_path: str):
    log.info(f"configuring workoutizer to run as system service")
    env_binaries = sys.executable
    wkz_executable = env_binaries[:env_binaries.find('python')] + "wkz"
    result = _run_ansible(
        playbook='configure_systemd.yml',
        variables={
            'address_plus_port': address_plus_port,
            'wkz_executable': wkz_executable,
            'wkz_service_path': wkz_service_path,
        }
    )
    if result == 0:
        log.info(f"Successfully configured workoutizer as systemd service. Run it with:\n"
                 f"systemctl start wkz.service")
    else:
        log.critical(f"Could not configure workoutizer as systemd service, see above errors.")
    return result


def _build_home():
    if os.path.isdir(WORKOUTIZER_DIR):
        if os.path.isfile(WORKOUTIZER_DB_PATH):
            log.info(f"Found existing workoutizer database at: {WORKOUTIZER_DB_PATH}\n")
            answer = input(f"Workoutizer could try to use the existing database instead of creating a new one.\n"
                           f"Note that this could lead to faulty behaviour because of mismatching applied\n"
                           f"migrations on this database.\n\n"
                           f"Do you want to use the existing database instead of creating a new one? [Y/n] ")
            if answer.lower() == 'y':
                log.info(f"keeping existing database at {WORKOUTIZER_DB_PATH}")
                return
            else:
                log.info(f"removed database at {WORKOUTIZER_DB_PATH}")
                os.remove(WORKOUTIZER_DB_PATH)
        _make_tracks_dir(TRACKS_DIR)
    else:
        os.mkdir(WORKOUTIZER_DIR)
        _make_tracks_dir(TRACKS_DIR)
    log.info(f"Workoutizer will store its database and track files at: {WORKOUTIZER_DIR}")


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


def _check_keys_exist(keys: List[str], arguments: dict):
    error_msg = "Could not find {key} in given command. Please provide {key} with command. See wkz -h for help."
    for key in keys:
        if key not in arguments.keys():
            log.critical(error_msg.format(key=key))
            quit()


def _setup_rpi_using_ansible(vendor_id: str, product_id: str, address_plus_port: str):
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
    variable_manager._extra_vars = {
        'vendor_id': vendor_id,
        'product_id': product_id,
        'address_plus_port': address_plus_port,
    }
    pbex = PlaybookExecutor(playbooks=[os.path.join(SETUP_DIR, 'setup_on_rpi.yml')], inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader, passwords={})
    pbex.run()


def _pip_install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def _run_ansible(playbook: str, variables: dict = None):
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
    pbex = PlaybookExecutor(playbooks=[os.path.join(SETUP_DIR, playbook)], inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader, passwords={})
    return pbex.run()


if __name__ == '__main__':
    cli()
