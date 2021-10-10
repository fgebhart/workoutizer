from huey import crontab
from huey.contrib.djhuey import periodic_task, task

from wkz import configuration as cfg
from wkz.device.mount import mount_device_and_collect_files
from wkz.watchdogs import trigger_device_watchdog, trigger_file_watchdog


@task()
def mount_device_and_collect_files_task():
    mount_device_and_collect_files()


@periodic_task(crontab(minute=f"*/{cfg.file_importer_interval}"))
def check_for_mounted_device():
    trigger_device_watchdog()


@periodic_task(crontab(minute=f"*/{cfg.file_collector_interval}"))
def check_for_new_activity_files():
    trigger_file_watchdog()
