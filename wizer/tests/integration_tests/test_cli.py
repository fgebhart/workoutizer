import builtins
import io
import os
import pytest

from workoutizer.__main__ import _wkz_as_service, _get_local_ip_address, _setup_rpi, _get_latest_version_of


def read_file_to_string(path):
    with open(path, "r") as f:
        content = f.read()
    return content


def patch_open(open_func, files):
    def open_patched(path, mode='r', buffering=-1, encoding=None,
                     errors=None, newline=None, closefd=True,
                     opener=None):
        if 'w' in mode and not os.path.isfile(path):
            files.append(path)
        return open_func(path, mode=mode, buffering=buffering,
                         encoding=encoding, errors=errors,
                         newline=newline, closefd=closefd,
                         opener=opener)

    return open_patched


@pytest.fixture(autouse=True)
def cleanup_files(monkeypatch):
    files = []
    monkeypatch.setattr(builtins, 'open', patch_open(builtins.open, files))
    monkeypatch.setattr(io, 'open', patch_open(io.open, files))
    yield
    for file in files:
        os.remove(file)


# TODO fix for running in github actions (test__ prefix was removed)
def setup_rpi(vendor_id, product_id, ip_port, wkz_mount_service_path, udev_rule_path, udev_rule_dir):
    # ensure udev folder exists
    if not os.path.isdir(udev_rule_dir):
        os.makedirs(udev_rule_dir)
    result = _setup_rpi(
        vendor_id=vendor_id,
        product_id=product_id,
        ip_port=ip_port,
    )
    assert result == 0
    assert os.path.isfile(wkz_mount_service_path)
    file = read_file_to_string(wkz_mount_service_path)
    assert ip_port in file
    os.remove(wkz_mount_service_path)
    assert os.path.isfile(udev_rule_path)
    file = read_file_to_string(udev_rule_path)
    assert vendor_id in file
    assert product_id in file
    os.remove(udev_rule_path)


# TODO fix for running in github actions (test__ prefix was removed)
def wkz_as_service(ip_port, wkz_service_path):
    # run with specified url
    result = _wkz_as_service(url=ip_port)
    assert result == 0
    assert os.path.isfile(wkz_service_path)
    file = read_file_to_string(wkz_service_path)
    assert ip_port in file
    os.remove(wkz_service_path)

    # run with specified url
    result = _wkz_as_service(url="")
    assert result == 0
    assert os.path.isfile(wkz_service_path)
    file = read_file_to_string(wkz_service_path)
    ip_port = f"{_get_local_ip_address()}:8000"
    assert ip_port in file
    os.remove(wkz_service_path)


def test__get_local_ip_address():
    ip_address = _get_local_ip_address()
    assert type(ip_address) == str
    assert len(ip_address) >= 8
    assert "." in ip_address


def test__get_latest_version_of():
    # should always be False since I always should have the recent one (github ci also)
    assert _get_latest_version_of("workoutizer") is False

    # should return the latest version, since it was down-pinned
    latest_version = _get_latest_version_of("django-leaflet")
    assert len(latest_version) > 4
    assert "." in latest_version
