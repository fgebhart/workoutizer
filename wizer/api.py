import os
import signal
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psutil

from wizer.file_helper.fit_collector import try_to_mount_device


log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    try:
        mount_path = try_to_mount_device()
        if mount_path:
            return Response("mounted and checked for files", status=status.HTTP_200_OK)
        else:
            log.error(f"could not mount device, no valid mount path available - got: {mount_path}")
            return Response("failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        log.error(f"could not mount device: {e}", exc_info=True)
        return Response("failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
