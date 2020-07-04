import logging
import os
import argparse
import subprocess
import sys
from typing import List
from logging.config import dictConfig

from django.core.management import execute_from_command_line

from workoutizer.logger import get_logging_for_wkz

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

    args = parser.parse_args()
    os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"
    if args.run == 'run':
        execute_from_command_line(["manage.py", "runserver"])
    elif args.run == 'init':
        execute_from_command_line(["manage.py", "collectstatic"])
        execute_from_command_line(["manage.py", "migrate"])
    elif args.setup_rpi:
        _check_keys_exist(keys=['product_id', 'vendor_id', 'address_plus_port'], arguments=args.setup_rpi)
        answer = input(f"Are you sure you want to setup your Raspberry Pi?\n\n"
                       f"This will copy the required udev rule and systemd service file\n"
                       f"to your system to enable automated mounting of your device.\n\n"
                       f"Start setup? [Y/n] ")
        if answer.lower() == 'y':
            log.debug(f"installing ansible...")
            _pip_install('ansible==2.9.10')
            log.debug(f"starting setup using ansible...")
            _setup_rpi_using_ansible(
                vendor_id=args.setup_rpi['vendor_id'],
                product_id=args.setup_rpi['product_id'],
                address_plus_port=args.setup_rpi['address_plus_port'],
            )
        else:
            log.info(f"Aborted.")
    elif args.manage:
        execute_from_command_line(["manage.py"] + args.manage)
    else:
        log.critical(f"wkz: error: unrecognized arguments")
        parser.print_help()
        return 1

    return 0


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
    error_msg = "Could not find {key} in given command. Please provide {key} with command like:\n" + example_rpi_cmd
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
    pbex = PlaybookExecutor(playbooks=[os.path.join(SETUP_DIR, 'setup_workoutizer.yml')], inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader, passwords={})
    pbex.run()


def _pip_install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':
    cli()
