import logging
import os
import signal

import psutil
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wkz.device.mount import garmin_device_connected
from wkz.tasks import mount_device_and_collect_files_task

log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    log.debug("received POST request for mounting garmin device")
    if garmin_device_connected():
        log.debug("found connected garmin device")
        # schedule huey task to answer response and work on mounting asynchronously
        mount_device_and_collect_files_task()
        return Response("Found device, will mount and collect fit files.", status=status.HTTP_200_OK)
    else:
        log.warning("No garmin device connected.")
        return Response("No Garmin device connected.", status=status.HTTP_200_OK)


@api_view(["POST"])
def stop_django_server(request):
    log.info("Stopped.")
    pid = os.getpid()
    parent = psutil.Process(pid)

    # first kill all child processes
    for child in parent.children(recursive=True):
        os.kill(child.pid, signal.SIGINT)

    # lastely kill the parent process
    os.kill(pid, signal.SIGINT)
    return Response("stopped", status=status.HTTP_200_OK)
