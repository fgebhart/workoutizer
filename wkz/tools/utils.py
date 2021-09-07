import datetime
import hashlib
import logging
import socket

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
