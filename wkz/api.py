import logging
import os
import signal

import psutil
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wkz import models
from wkz.device.mount import FailedToMountDevice, wait_for_device_and_mount
from wkz.parser.fit_collector import collect_fit_files_from_device

log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    # TODO: run function non-blocking!?
    log.info("received POST request for mounting garmin device")
    try:
        path_to_garmin_device = wait_for_device_and_mount()
        settings = models.get_settings()
        n_files_collected = collect_fit_files_from_device(
            path_to_garmin_device=path_to_garmin_device,
            target_location=settings.path_to_trace_dir,
            delete_files_after_import=settings.delete_files_after_import,
        )
        return Response(f"Mounted device and collected {n_files_collected} fit files.", status=status.HTTP_200_OK)
    except FailedToMountDevice:
        return Response("Failed to mount device.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
