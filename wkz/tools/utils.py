import logging
import socket
import hashlib
import datetime

import pytz
from django.conf import settings

log = logging.getLogger(__name__)

timestamp_format = "%Y-%m-%dT%H:%M:%SZ"


def sanitize(text):
    return str(text).lower().replace(" ", "-").replace("/", "-")


def calc_md5(file) -> str:
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def cut_list_to_have_same_length(list1, list2, mode="cut beginning", modify_only_list2=False):
    diff = len(list1) - len(list2)
    if mode == "cut beginning":
        if diff < 0:
            list2 = list2[abs(diff) :]
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
        raise NotImplementedError("mode not implemented")
    return list1, list2


def timestamp_to_local_time(timestamp: int):
    return pytz.utc.localize(datetime.datetime.fromtimestamp(timestamp), is_dst=False).astimezone(
        pytz.timezone(settings.TIME_ZONE)
    )


def remove_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def limit_string(string: str, max_length: int):
    string = str(string)
    if max_length >= len(string):
        return string
    else:
        return f"{string[:(int(max_length/2))]}...{string[(-int(max_length/2)):]}"


def get_local_ip_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def files_are_same(file_a: str, file_b: str) -> bool:
    if calc_md5(file_a) == calc_md5(file_b):
        return True
    else:
        return False
