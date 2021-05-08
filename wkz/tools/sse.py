import re
import logging

from django_eventstream import send_event


log = logging.getLogger(__name__)


def clean_html(raw_html):
    cleaner = re.compile("<.*?>")
    cleantext = re.sub(cleaner, "", raw_html)
    return cleantext


def send(text: str, color: str, log_level: str = "DEBUG"):
    """Server Sent Event"""
    log_level = getattr(logging, log_level)
    log.log(log_level, clean_html(text))
    send_event("event", "message", {"text": text, "color": color})
