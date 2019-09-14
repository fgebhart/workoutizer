import logging

log = logging.getLogger('wizer.utils')


def sanitize(text):
    return str(text).lower().replace(" ", "-")
