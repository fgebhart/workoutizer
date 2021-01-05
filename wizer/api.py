import os
import signal
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import psutil

from wizer.file_helper.fit_collector import try_to_mount_device, FitCollector, unmount_device_using_gio
from wizer import models


log = logging.getLogger(__name__)


@api_view(["POST"])
def mount_device_endpoint(request):
    try:
        # 1. mount device
        mount_path = try_to_mount_device()
        if mount_path:
            settings = models.get_settings()
            # 2. collect fit files from device to trace dir
            fit_collector = FitCollector(
                path_to_garmin_device=settings.path_to_garmin_device,
                target_location=settings.path_to_trace_dir,
                delete_files_after_import=settings.delete_files_after_import,
            )
            fit_collector.copy_fit_files()
            # no need to trigger file importer here anymore since watchdog
            # will automatically realize new files and trigger the file importer

            # 4. once collecting and importing was successful unmount device
            unmount_device_using_gio(settings.path_to_garmin_device)

            return Response("mounted and checked for files", status=status.HTTP_200_OK)
        else:
            log.error(f"could not mount device, no valid mount path available - got: {mount_path}")
            return Response("failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        log.error(f"could not mount device: {e}")
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
