import time
from pathlib import Path
import operator

from lxml import etree

from wkz.demo import copy_demo_fit_files_to_track_dir
from wkz import models
from wkz.watchdogs import trigger_device_watchdog, trigger_file_watchdog
from tests.utils import delayed_assertion


def test__start_file_importer_watchdog_basic(db, tmp_path, test_data_dir, demo_data_dir, fit_file_a):
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    # update path_to_trace_dir in db accordingly, since file importer will read it from the db
    settings = models.get_settings()
    trace_dir = tmp_path / "trace_dir"
    trace_dir.mkdir()
    assert trace_dir.is_dir()
    settings.path_to_trace_dir = trace_dir
    settings.save()

    # put an activity fit file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=demo_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=[fit_file_a],
    )
    assert (Path(trace_dir) / fit_file_a).is_file()

    trigger_file_watchdog()
    # watchdog should now have triggered the file imported and activity should be in db
    delayed_assertion(models.Activity.objects.count, operator.eq, 1)
    delayed_assertion(models.BestSection.objects.count, operator.gt, 0)
    bs1 = models.BestSection.objects.count()

    # now put a activity GPX file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=test_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=["example.gpx"],
    )
    path_to_gpx = Path(trace_dir) / "example.gpx"
    assert path_to_gpx.is_file()
    # ensure file is a well-formed xml
    etree.parse(str(path_to_gpx))

    trigger_file_watchdog()

    delayed_assertion(models.Activity.objects.count, operator.eq, 2)
    delayed_assertion(models.BestSection.objects.count, operator.gt, bs1)
    bs2 = models.BestSection.objects.count()

    # create a non fit/gpx file to verify it won't be imported
    dummy_file = trace_dir / "fake_activity.txt"
    dummy_file.write_text("not a real activity", encoding="utf-8")

    # check that the dummy file was actually created
    assert Path(dummy_file).is_file()

    # but assert that the number of activities and best sections did not increase
    delayed_assertion(models.Activity.objects.count, operator.eq, 2)
    delayed_assertion(models.BestSection.objects.count, operator.eq, bs2)


def test_fake_device(db, fake_device, device_dir, activity_dir, fit_file):
    # initialize fake device
    device = fake_device(activity_files=[fit_file])

    settings = models.Settings.objects.get()
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

    trigger_device_watchdog()
    assert f"Device Watchdog: {invalid_dir} is not a valid directory." in caplog.text


def test__start_file_importer_watchdog__missing_dir(db, caplog):
    invalid_dir = "/some/random/non_existent/path/"

    settings = models.get_settings()
    settings.path_to_trace_dir = invalid_dir
    settings.save()

    trigger_file_watchdog()
    assert f"File Watchdog: {invalid_dir} is not a valid directory." in caplog.text


def test__start_device_watchdog__collect_files(
    db, fake_device, device_dir, activity_dir, fit_file_a, fit_file_b, tmp_path
):
    # initialize fake device with two fit files
    device = fake_device(activity_files=[fit_file_a, fit_file_b])

    settings = models.get_settings()
    mount_path = Path(settings.path_to_garmin_device)
    trace_dir = tmp_path / "random_trace_dir"
    trace_dir.mkdir()
    settings.path_to_trace_dir = trace_dir
    settings.save()

    # verify mount path exists
    assert mount_path.is_dir()

    # ensure fit files are not already present in trace dir
    assert not (trace_dir / "garmin" / fit_file_a).is_file()
    assert not (trace_dir / "garmin" / fit_file_b).is_file()

    # now mount device which contains fit files
    device.mount()

    # start device watch dog
    trigger_device_watchdog()

    assert (device.activity_path_on_device / fit_file_a).is_file()
    assert (device.activity_path_on_device / fit_file_b).is_file()

    # verify the fit files are present on the mounted device
    assert (mount_path / device_dir / activity_dir / fit_file_a).is_file()
    assert (mount_path / device_dir / activity_dir / fit_file_b).is_file()

    # verify that the fit files are now present in the trace dir
    delayed_assertion((trace_dir / "garmin" / fit_file_a).is_file, operator.is_, True)
    delayed_assertion((trace_dir / "garmin" / fit_file_b).is_file, operator.is_, True)


def test_device_and_file_importer_watchdog(
    db, tmpdir, test_data_dir, demo_data_dir, fake_device, device_dir, activity_dir, fit_file_a, fit_file_b
):
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    device = fake_device(activity_files=[fit_file_a, fit_file_b])

    settings = models.get_settings()
    mount_path = Path(settings.path_to_garmin_device)
    trace_dir = Path(settings.path_to_trace_dir)
    settings.path_to_trace_dir = trace_dir
    settings.save()

    # verify mount path exists
    assert mount_path.is_dir()

    # ensure fit files are not already present in trace dir
    assert not (trace_dir / fit_file_a).is_file()
    assert not (trace_dir / fit_file_b).is_file()

    # mounting the device will:
    #  1. trigger device watchdog to copy fit files to trace dir, what in turn will
    #  2. trigger file importer watchdog to import the fit files into workoutizer activities
    device.mount()

    # start device watchdog
    trigger_device_watchdog()

    # verify the fit files are present on the mounted device
    assert (mount_path / device_dir / activity_dir / fit_file_a).is_file()
    assert (mount_path / device_dir / activity_dir / fit_file_b).is_file()

    # verify that the fit files are now present in the trace dir
    delayed_assertion((trace_dir / "garmin" / fit_file_a).is_file, operator.is_, True)
    delayed_assertion((trace_dir / "garmin" / fit_file_b).is_file, operator.is_, True)

    # start file watchdog
    trigger_file_watchdog()

    # check that the activities got imported
    delayed_assertion(models.Activity.objects.count, operator.eq, 2)
    delayed_assertion(models.BestSection.objects.count, operator.gt, 2)


def test_file_importer__with_path_being_changed(db, tmp_path, demo_data_dir, fit_file_a, fit_file_b):
    dummy_path_settings = models.Settings(path_to_trace_dir=tmp_path / "dummy_path")
    dummy_path_settings.save()
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    # assume we have two directories: an empty directory and one with activities
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    assert empty_dir.is_dir()
    assert not any(empty_dir.iterdir())  # = no file in empty dir

    dir_with_files = tmp_path / "dir_with_files"
    dir_with_files.mkdir()
    assert dir_with_files.is_dir()
    copy_demo_fit_files_to_track_dir(
        source_dir=demo_data_dir,
        targe_dir=dir_with_files,
        list_of_files_to_copy=[fit_file_a],
    )
    assert (Path(dir_with_files) / fit_file_a).is_file()
    assert any(dir_with_files.iterdir())  # dir_with_files contains a file

    # first, file watchdog is watching the empty dir (note, chaning settings will re-trigger watchdog)
    dummy_path_settings.path_to_trace_dir = empty_dir
    dummy_path_settings.save()

    # since watchdog is watching empty dir, activity count should still be 0
    delayed_assertion(models.Activity.objects.count, operator.eq, 0)
    # now change the settings path to point to the dir_with_files
    dummy_path_settings.path_to_trace_dir = dir_with_files
    dummy_path_settings.save()

    # watchdog should automatically pick up the new path, start watching the new dir, find the
    # given activity file (even if it was added before starting to watch if) and import it
    delayed_assertion(models.Activity.objects.count, operator.eq, 1)

    # now also add an activity file to the empty dir and check that watchdog does not get triggered
    copy_demo_fit_files_to_track_dir(
        source_dir=demo_data_dir,
        targe_dir=empty_dir,
        list_of_files_to_copy=[fit_file_b],
    )
    time.sleep(3)
    delayed_assertion(models.Activity.objects.count, operator.ne, 2)
