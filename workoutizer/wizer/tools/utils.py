import logging

log = logging.getLogger('wizer.utils')


def sanitize(text):
    return str(text).lower().replace(" ", "-")


def convert_timedelta_to_hours(td):
    return int(td.total_seconds() / 60)
