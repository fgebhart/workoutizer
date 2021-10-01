import logging
import os
import signal

import psutil
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wkz.device.mount import (
    garmin_device_connected,
    try_to_mount_device_and_collect_fit_files,
)

log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    log.debug("received POST request for mounting garmin device")
    if garmin_device_connected():
        log.debug("found connected garmin device")
        task = try_to_mount_device_and_collect_fit_files()
        n_files_collected = task()
        return Response(f"Mounted device and collected {n_files_collected} fit files.", status=status.HTTP_200_OK)
    else:
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
