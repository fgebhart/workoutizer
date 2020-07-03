import os
import argparse
import configparser

from django.core.management import execute_from_command_line

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.ini')

# read config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
ip_address = config.get("WORKOUTIZER", "local_ip_address")


def cli():
    parser = argparse.ArgumentParser(description='Workoutizer - Workout Organizer')
    command_group = parser.add_mutually_exclusive_group()
    command_group.add_argument('run', help='runs the workoutizer application', nargs='?')
    command_group.add_argument('init', help='collects static files and migrates the db schema to a newer version',
                               nargs='?')
    parser.add_argument("-m", "--manage", help="pass arguments to django's manage.py", nargs='+')

    args = parser.parse_args()
    os.environ["DJANGO_SETTINGS_MODULE"] = "workoutizer.settings"
    if args.run == 'run':
        execute_from_command_line(["manage.py", "runserver", ip_address])
    elif args.run == 'init':
        execute_from_command_line(["manage.py", "collectstatic"])
        execute_from_command_line(["manage.py", "migrate"])
    elif args.manage:
        execute_from_command_line(["manage.py"] + args.manage)
    else:
        print(f"wkz: error: unrecognized arguments")
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    cli()
