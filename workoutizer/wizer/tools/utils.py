import logging
import hashlib

log = logging.getLogger('wizer.utils')


def sanitize(text):
    return str(text).lower().replace(" ", "-")


def calc_md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
