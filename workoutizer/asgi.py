"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

import django_eventstream
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            [
                re_path(
                    r"^events/",
                    AuthMiddlewareStack(URLRouter(django_eventstream.routing.urlpatterns)),
                    {"channels": ["event"]},
                ),
                re_path(r"", get_asgi_application()),
            ]
        ),
    }
)
