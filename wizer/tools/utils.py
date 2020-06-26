import logging
import hashlib
import datetime

import pytz

from django.conf import settings

log = logging.getLogger(__name__)

timestamp_format = "%Y-%m-%dT%H:%M:%SZ"


def sanitize(text):
    return str(text).lower().replace(" ", "-")


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def remove_nones_from_string(string: str):
    if "None, " in string:
        string = string.replace("None, ", "")
    if ", None" in string:
        string = string.replace(", None", "")
    elif "None " in string:
        string = string.replace("None ", "")
    elif "None" in string:
        string = string.replace("None", "")
    return string


def remove_nones_from_list(list: list):
    return [x for x in list if x is not None]


def ensure_lists_have_same_length(list1, list2, mode="cut beginning", modify_only_list2=False):
    diff = len(list1) - len(list2)
    if mode == "cut beginning":
        if diff < 0:
            list2 = list2[abs(diff):]
        elif diff > 0:
            if not modify_only_list2:
                list1 = list1[diff:]
    elif mode == "fill end":
        if diff < 0:  # last 2 is larger
            if not modify_only_list2:
                list1 = list1 + abs(diff) * [list1[-1]]
        elif diff > 0:  # list 1 is larger
            list2 = list2 + diff * [list2[-1]]
    else:
        raise NotImplementedError('mode not implemented')
    return list1, list2


def timestamp_to_local_time(timestamp: int):
    return pytz.utc.localize(datetime.datetime.fromtimestamp(timestamp), is_dst=False).astimezone(
        pytz.timezone(settings.TIME_ZONE))


def remove_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)