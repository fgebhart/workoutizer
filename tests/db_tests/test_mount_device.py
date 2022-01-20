import logging
import os
import shutil
from pathlib import Path

from tests.unit_tests.device.test_mount import (
    lsusb_device_not_ready_to_be_mounted,
    lsusb_no_garmin_device_at_all,
    lsusb_ready_to_be_mounted_device,
)
from wkz import models


def test_mount_device_and_collect_files(db, monkeypatch, caplog, tmpdir):
    caplog.set_level(logging.DEBUG, logger="wkz.device.mount")
    caplog.set_level(logging.DEBUG, logger="wkz.io.fit_collector")
    # mock huey task away to actually test content of function mount_device_and_collect_files
    from workoutizer import settings as django_settings

    def task(func):
        return func

    # first mock decorator HUEY.task with dummy function
    monkeypatch.setattr(django_settings.HUEY, "task", task)
    # then import actual function (which in turn applies mocked decorator)

    from wkz.device.mount import (
        _wait_for_device_and_mount,
        mount_device_and_collect_files,
    )

    # run actual function to be tested
    mount_device_and_collect_files()

    # without futher mocking this would print and failed message
    assert "Failed to mount device: No 'lsusb' command available on your system." in caplog.text

    # now mock even other inner functions in order to have the mounting & fit file collecting proceed
    from wkz.device import mount

    def _get_lsusb_output():
        return lsusb_no_garmin_device_at_all

    monkeypatch.setattr(mount, "_get_lsusb_output", _get_lsusb_output)

    # in case the output of lsusb does not contain "Garmin" a error is raised
    mount_device_and_collect_files()
    assert "Failed to mount device: Expected output of 'lsusb' to contain string 'Garmin'." in caplog.text

    # now mock the lsusb output with a real world example
    from wkz.device import mount

    def _get_lsusb_output():
        return lsusb_device_not_ready_to_be_mounted

    monkeypatch.setattr(mount, "_get_lsusb_output", _get_lsusb_output)

    # also mock the waiting time to speed up the test execution
    from wkz.device import mount

    monkeypatch.setattr(mount, "WAIT", 0.1)

    mount_device_and_collect_files()
    assert "checking device to be ready for mount..." in caplog.text
    assert "device is not ready for mounting yet, waiting 0.1 seconds..." in caplog.text
    assert "could not mount device within time window of 0.5 seconds." in caplog.text
    assert "Failed to mount device: Unable to mount device after 5 retries, with 0.1s delay each." in caplog.text

    # now test the mounting of a device which is ready to be mounted
    from wkz.device import mount

    def _get_lsusb_output():
        return lsusb_ready_to_be_mounted_device

    monkeypatch.setattr(mount, "_get_lsusb_output", _get_lsusb_output)
    mount_device_and_collect_files()
    assert "checking device to be ready for mount..." in caplog.text
    assert "device seems to be ready for mount, mounting..." in caplog.text
    assert "trying to determine device type for device at: /dev/bus/usb/001/004..." in caplog.text
    # hacky way to test both unix and mac world. Mac lacks udev and thus the second assertion should pass
    try:
        assert "Failed to mount device: Could not determine device type. Device is neither MTP nor BLOCK." in caplog.text
    except AssertionError:
        assert "Failed to mount device: Your system seems to lack the udev utility." in caplog.text

    # now also mock _determine_type_and_mount to return the path to the mounted device
    path_to_device = tmpdir

    def _determine_type_and_mount(path):
        device_type = mount.DeviceType.MTP
        return device_type

    monkeypatch.setattr(mount, "_determine_type_and_mount", _determine_type_and_mount)

    # also prepare a fake dummy path (to a fake device) from where the fit files would be imported from
    fake_device_dir = os.path.join(path_to_device, "mtp:host", "Primary", "GARMIN", "Activity")
    os.makedirs(fake_device_dir)

    settings = models.get_settings()
    settings.path_to_garmin_device = fake_device_dir
    path_to_trace_dir = tmpdir / "trace_dir"
    settings.path_to_trace_dir = path_to_trace_dir
    settings.save()

    # put a fit file into fake_device_dir and verified it being collected
    fit = "2019-09-18-16-02-35.fit"
    shutil.copy2(os.path.join(django_settings.INITIAL_TRACE_DATA_DIR, fit), fake_device_dir)
    mount_device_and_collect_files()
    assert "checking device to be ready for mount..." in caplog.text
    assert "device seems to be ready for mount, mounting..." in caplog.text
    assert "unable to mount device of type: DeviceType.MTP, will retry 1 more time(s)..." in caplog.text
    assert "could not mount device within time window of 0.5 seconds." in caplog.text
    assert "Failed to mount device: Unable to mount device after 5 retries, with 0.1s delay each." in caplog.text

    # mock the default path of EXPECTED_MTP_DEVICE_PATH since for testing we cannot ensure to construct a path at /var
    monkeypatch.setattr(mount, "EXPECTED_MTP_DEVICE_PATH", Path(tmpdir))

    mount_device_and_collect_files()
    assert "sanity check to see if a device is already mounted..." in caplog.text
    assert f"found mounted garmin device at: {path_to_device}, will skip mounting" in caplog.text
    assert f"looking for new activity files in garmin device at {path_to_device}" in caplog.text
    assert "copied file" in caplog.text

    # verify that fit file got collected
    assert Path(path_to_trace_dir / "garmin" / fit).is_file()

    # we could also run _wait_for_device_and_mount to avoid the skipped mounting
    _wait_for_device_and_mount()
    assert "checking device to be ready for mount..." in caplog.text
    assert "device seems to be ready for mount, mounting..." in caplog.text
    assert f"successfully mounted device at: {path_to_device}" in caplog.text
