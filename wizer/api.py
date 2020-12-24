import os
import signal
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psutil


from wizer.file_helper.fit_collector import try_to_mount_device
from wizer.file_importer import FileImporter
from wizer import models


log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    mount_path = try_to_mount_device()
    if mount_path:
        FileImporter(models=models, importing_demo_data=False, single_run=True)
        return Response("mounted", status=status.HTTP_200_OK)
    else:
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
    return Response("failed", status=status.HTTP_200_OK)
