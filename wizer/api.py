import os
import signal
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psutil


from wizer.file_helper.fit_collector import try_to_mount_device, FitCollector
from wizer import models


log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    mount_path = try_to_mount_device()
    settings = models.Settings.objects.get_or_create(pk=1)[0]
    if mount_path:
        fit_collector = FitCollector(
            path_to_garmin_device=settings.path_to_garmin_device,
            target_location=settings.path_to_trace_dir,
            delete_files_after_import=settings.delete_files_after_import,
        )
        fit_collector.copy_fit_files()
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
        os.kill(child, signal.SIGINT)
    # lastely kill the parent process
    os.kill(pid, signal.SIGINT)
    return Response("failed", status=status.HTTP_200_OK)
