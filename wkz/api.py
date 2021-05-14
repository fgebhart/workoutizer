import os
import signal
import logging
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import status
import psutil

from wkz.file_helper.fit_collector import try_to_mount_device
from wkz.tools import sse
from wkz.file_importer import run_file_importer
from wkz import models


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


@api_view(["POST"])
def reimport_activities(request):
    template = "settings/reimport.html"
    settings = models.get_settings()
    if Path(settings.path_to_trace_dir).is_dir():
        run_file_importer(models, importing_demo_data=False, reimporting=True, as_huey_task=True)
    else:
        sse.send(f"'{settings.path_to_trace_dir}' is not a valid path.", "red")
    return render(request, template_name=template)
