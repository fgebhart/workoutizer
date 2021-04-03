import time
from pathlib import Path
import operator

from wizer.watchdogs import _start_file_importer_watchdog, _start_device_watchdog
from wizer.file_importer import copy_demo_fit_files_to_track_dir
from wizer import models

TIMEOUT = 10


def condition(func, operator, right, timeout: int = TIMEOUT) -> bool:
    """
    Helper function to check if a condition evaluates to True in a given
    time range until the timeout.
    """
    for _ in range(timeout):
        if operator(func(), right):
            return True
        time.sleep(1)
    return False


def test__start_file_importer_watchdog_basic(transactional_db, tmp_path, test_data_dir, demo_data_dir, fit_file_a):
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    # update path_to_trace_dir in db accordingly, since import_activity_files will read it from the db
    settings = models.get_settings()
    trace_dir = tmp_path / "trace_dir"
    trace_dir.mkdir()
    assert trace_dir.is_dir()
    settings.path_to_trace_dir = trace_dir
    settings.save()

    _start_file_importer_watchdog(trace_dir, models=models)

    # put an activity fit file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=demo_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=[fit_file_a],
    )
    assert (Path(trace_dir) / fit_file_a).is_file()

    # watchdog should now have triggered the file imported and activity should be in db
    assert condition(models.Activity.objects.count, operator.eq, 1)
    assert condition(models.BestSection.objects.count, operator.gt, 0)
    bs1 = models.BestSection.objects.count()

    # now put a activity GPX file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=test_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=["example.gpx"],
    )

    assert condition(models.Activity.objects.count, operator.eq, 2)
    assert condition(models.BestSection.objects.count, operator.gt, bs1)
    bs2 = models.BestSection.objects.count()

    # create a non fit/gpx file to verify it won't be imported
    dummy_file = trace_dir / "fake_activity.txt"
    dummy_file.write_text("not a real activity", encoding="utf-8")

    # check that the dummy file was actually created
    assert Path(dummy_file).is_file()

    # but assert that the number of activities and best sections did not increase
    assert condition(models.Activity.objects.count, operator.eq, 2)
    assert condition(models.BestSection.objects.count, operator.eq, bs2)


def test_fake_device(db, fake_device, device_dir, activity_dir, fit_file):
    # initialize fake device
    device = fake_device(activity_files=[fit_file])

    settings = models.get_settings()
    mount_path = Path(settings.path_to_garmin_device)
    # once fake device is initialized, mount path should be available
    assert mount_path.is_dir()

    # now mount the fake device, which should also contain a fit file
    device.mount()

    assert (mount_path / device_dir).is_dir()
    assert (mount_path / device_dir / activity_dir).is_dir()
    assert (mount_path / device_dir / activity_dir / fit_file).is_file()

    # check that mounting again does not have any effect
    device.mount()
    assert (mount_path / device_dir / activity_dir / fit_file).is_file()

    # unmount device again and verify dirs are gone
    device.unmount()
    assert not (mount_path / device_dir).is_dir()
    assert not (mount_path / device_dir / activity_dir / fit_file).is_file()

    # check that unmounting again does not have any effect
    device.unmount()
    assert not (mount_path / device_dir).is_dir()
    assert not (mount_path / device_dir / activity_dir / fit_file).is_file()

    # and again mounting should also work
    device.mount()
    assert (mount_path / device_dir / activity_dir / fit_file).is_file()


def test__start_device_watchdog__missing_dir(db, caplog):
    invalid_dir = "/some/random/non_existent/path/"

    settings = models.get_settings()
    settings.path_to_garmin_device = invalid_dir
    settings.save()

    _start_device_watchdog(invalid_dir, settings.path_to_trace_dir, settings.delete_files_after_import)
    assert f"Device mount path {invalid_dir} does not exist. Device watchdog is disabled." in caplog.text


def test__start_file_importer_watchdog__missing_dir(db, caplog):
    invalid_dir = "/some/random/non_existent/path/"

    settings = models.get_settings()
    settings.path_to_trace_dir = invalid_dir
    settings.save()

    _start_file_importer_watchdog(invalid_dir, models=models)
    assert f"Path to trace dir {invalid_dir} does not exist. File Importer watchdog is disabled." in caplog.text


def test__start_device_watchdog(transactional_db, fake_device, device_dir, activity_dir, fit_file_a, fit_file_b):
    # initialize fake device with two fit files
    device = fake_device(activity_files=[fit_file_a, fit_file_b])

    settings = models.get_settings()
    mount_path = Path(settings.path_to_garmin_device)
    trace_dir = Path(settings.path_to_trace_dir)

    # verify mount path exists
    assert mount_path.is_dir()

    # ensure fit files are not already present in trace dir
    assert not (trace_dir / fit_file_a).is_file()
    assert not (trace_dir / fit_file_b).is_file()

    # start device watch dog
    _start_device_watchdog(mount_path, trace_dir, settings.delete_files_after_import)

    # now mount device which contains fit files
    device.mount()

    # verify the fit files are present on the mounted device
    assert (mount_path / device_dir / activity_dir / fit_file_a).is_file()
    assert (mount_path / device_dir / activity_dir / fit_file_b).is_file()

    # verify that the fit files are now present in the trace dir
    assert condition((trace_dir / "garmin" / fit_file_a).is_file, operator.is_, True)
    assert condition((trace_dir / "garmin" / fit_file_b).is_file, operator.is_, True)


def test_device_and_file_importer_watchdog(
    transactional_db, tmpdir, test_data_dir, demo_data_dir, fake_device, device_dir, activity_dir, fit_file_a, fit_file_b
):
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    device = fake_device(activity_files=[fit_file_a, fit_file_b])

    settings = models.get_settings()
    mount_path = Path(settings.path_to_garmin_device)
    trace_dir = Path(settings.path_to_trace_dir)

    # verify mount path exists
    assert mount_path.is_dir()

    # ensure fit files are not already present in trace dir
    assert not (trace_dir / fit_file_a).is_file()
    assert not (trace_dir / fit_file_b).is_file()

    # start watchdogs
    _start_device_watchdog(mount_path, trace_dir, settings.delete_files_after_import)
    _start_file_importer_watchdog(trace_dir, models=models)

    # mounting the device will:
    #  1. trigger device watchdog to copy fit files to trace dir, what in turn will
    #  2. trigger file importer watchdog to import the fit files into workoutizer activities
    device.mount()

    # verify the fit files are present on the mounted device
    assert (mount_path / device_dir / activity_dir / fit_file_a).is_file()
    assert (mount_path / device_dir / activity_dir / fit_file_b).is_file()

    # verify that the fit files are now present in the trace dir
    assert condition((trace_dir / "garmin" / fit_file_a).is_file, operator.is_, True)
    assert condition((trace_dir / "garmin" / fit_file_b).is_file, operator.is_, True)

    # check that the activities got imported
    assert condition(models.Activity.objects.count, operator.eq, 2)
    assert condition(models.BestSection.objects.count, operator.gt, 2)
