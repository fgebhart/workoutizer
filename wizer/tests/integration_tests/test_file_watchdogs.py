import time
from pathlib import Path

from wizer.watchdogs import _start_file_importer_watchdog, _start_device_watchdog
from wizer.file_importer import copy_demo_fit_files_to_track_dir
from wizer import models


def test__start_file_importer_watchdog(transactional_db, tmpdir, test_data_dir, demo_data_dir):
    assert models.Activity.objects.count() == 0
    assert models.BestSection.objects.count() == 0

    trace_dir = tmpdir.mkdir("trace_dir")

    # update path_to_trace_dir in db accordingly, since import_activity_files will read it from the db
    settings = models.get_settings()
    settings.path_to_trace_dir = trace_dir
    settings.save()

    _start_file_importer_watchdog(trace_dir, models=models)

    # put an activity fit file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=demo_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=["cycling_bad_schandau.fit"],
    )

    # wait for activity to be imported
    time.sleep(3)
    assert models.Activity.objects.count() == 1
    bs1 = models.BestSection.objects.count()
    assert bs1 > 0

    # now put a activity GPX file into the watched dir
    copy_demo_fit_files_to_track_dir(
        source_dir=test_data_dir,
        targe_dir=trace_dir,
        list_of_files_to_copy=["example.gpx"],
    )

    # wait for activity to be imported
    time.sleep(3)
    assert models.Activity.objects.count() == 2
    bs2 = models.BestSection.objects.count()
    assert bs2 > bs1

    # create a non fit/gpx file to verify it won't be imported
    dummy_file = trace_dir / "fake_activity.txt"
    dummy_file.write_text("not a real activity", encoding="utf-8")

    # check that the dummy file was actually created
    assert Path(dummy_file).is_file()

    # same as above, provide some time for the potential import
    time.sleep(3)
    # but assert that the number of activities and best sections did not increase
    assert models.Activity.objects.count() == 2
    assert models.BestSection.objects.count() == bs2


def test__start_device_watchdog(transactional_db, tmp_path, fake_device):
    mount_path = tmp_path / "mount_path"
    mount_path.mkdir()
    assert mount_path.is_dir()

    settings = models.get_settings()
    settings.path_to_garmin_device = mount_path
    settings.save()

    device = fake_device(mount_path)

    _start_device_watchdog(mount_path, models=models)

    # now mount the fake device
    device.mount(activity_files=["2019-09-14-17-22-05.fit"])

    time.sleep(3)
    assert (mount_path / "MY_DEVICE").is_dir()
    device.unmount()

    assert not (mount_path / "MY_DEVICE").is_dir()
