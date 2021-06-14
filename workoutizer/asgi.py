"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

import django_eventstream
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            [
                url(
                    r"^events/",
                    AuthMiddlewareStack(URLRouter(django_eventstream.routing.urlpatterns)),
                    {"channels": ["event"]},
                ),
                url(r"", get_asgi_application()),
            ]
        ),
    }
)
