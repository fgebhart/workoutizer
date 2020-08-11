import logging
import hashlib
import datetime

import pytz
import numpy as np
import pandas as pd
from django.conf import settings

log = logging.getLogger(__name__)

timestamp_format = "%Y-%m-%dT%H:%M:%SZ"


def sanitize(text):
    return str(text).lower().replace(" ", "-").replace("/", "-")


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


def cut_list_to_have_same_length(list1, list2, mode="cut beginning", modify_only_list2=False):
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


def extend_list_to_have_length(length: int, input_list: list):
    if not input_list:
        return input_list
    arr = [input_list[int(x)] for x in np.arange(0, len(input_list), (len(input_list) / length))]
    s = pd.Series(arr)
    s = s.where(~s.duplicated(keep="first"), np.nan).interpolate()
    s = s[:length]
    log.debug(f"length of generated list: {len(s)} vs given length: {length}")
    assert len(s) == length
    return list(s)


def convert_list_to_km(list_in_meter: list):
    return [distance_in_meter / 1000 for distance_in_meter in list_in_meter]
