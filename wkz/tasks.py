from huey import crontab
from huey.contrib.djhuey import periodic_task

from wkz.watchdogs import trigger_device_watchdog, trigger_file_watchdog
from wkz import configuration as cfg


@periodic_task(crontab(minute=f"*/{cfg.file_importer_interval}"))
def check_for_mounted_device():
    trigger_device_watchdog()


@periodic_task(crontab(minute=f"*/{cfg.file_collector_interval}"))
def check_for_new_activity_files():
    trigger_file_watchdog()
