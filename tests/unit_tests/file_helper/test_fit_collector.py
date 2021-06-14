import shutil
from pathlib import Path

from wkz.file_helper.fit_collector import FitCollector, _find_activity_sub_dir_in_path


def test__find_activity_sub_dir_in_path(tmp_path):

    # desired sub dir is in first level
    d = tmp_path / "first"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="first", path=tmp_path, depth=1) == str(d)

    # desired sub dir is in first level and algorithm should not be case sensitive
    d = tmp_path / "UPPER"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="upper", path=tmp_path, depth=1).lower() == str(d).lower()

    # desired sub dir is in second level
    d = tmp_path / "first" / "second"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="second", path=tmp_path, depth=2) == str(d)

    # desired sub dir is in third level
    d = tmp_path / "first" / "second" / "third"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="third", path=tmp_path, depth=3) == str(d)

    # if dir in fourth level is searched for but depth is specified as 3 only, function should return False
    d = tmp_path / "first" / "second" / "third" / "fourth"
    d.mkdir()
    assert _find_activity_sub_dir_in_path(name_of_dir="fourth", path=tmp_path, depth=3) is False

    # a more realistic example
    d = tmp_path / "mtp:something" / "GARMIN" / "Primary" / "Activity"
    d.mkdir(parents=True)
    assert _find_activity_sub_dir_in_path(name_of_dir="Activity", path=tmp_path, depth=4) == str(d)


def test_deleting_fit_files_after_coying(tmp_path, demo_data_dir):
    # path to garmin device
    garmin = tmp_path / "garmin"
    garmin.mkdir()

    # activity dir on device
    activity = garmin / "Activity"
    activity.mkdir()

    # path to target activity dir
    target = tmp_path / "target"
    target.mkdir()

    # copy file from demo data dir to activity dir "on device"
    fit_file_1 = Path(activity) / "test_fit.fit"
    source_fit_1 = Path(demo_data_dir) / "cycling_bad_schandau.fit"
    shutil.copy(source_fit_1, fit_file_1)

    assert fit_file_1.is_file()

    # first collect fit file without deleting source file
    fit_collector = FitCollector(garmin, target, delete_files_after_import=False)
    fit_collector.copy_fit_files()

    # verify fit file got copied
    assert (target / "garmin" / "test_fit.fit").is_file()

    # file "on device" did not get deleted
    assert (activity / "test_fit.fit").is_file()

    fit_file_2 = Path(activity) / "test_fit_2.fit"
    source_fit_2 = Path(demo_data_dir) / "2020-08-28-11-57-10.fit"
    shutil.copy(source_fit_2, fit_file_2)
    assert fit_file_2.is_file()

    # now collect it with deleting it
    fit_collector = FitCollector(garmin, target, delete_files_after_import=True)
    fit_collector.copy_fit_files()

    # verify fit file got copied
    assert (target / "garmin" / "test_fit_2.fit").is_file()

    # file "on device" got deleted
    assert not (activity / "test_fit_2.fit").is_file()


def test_collecting_fit_files_with_upper_case_ending(tmp_path, demo_data_dir):
    # path to garmin device
    garmin = tmp_path / "garmin"
    garmin.mkdir()

    # activity dir on device
    activity = garmin / "Activity"
    activity.mkdir()

    # path to target activity dir
    target = tmp_path / "target"
    target.mkdir()

    # copy demo fit file and use upper case file ending
    fit_file = Path(activity) / "test_fit.FIT"
    source_fit = Path(demo_data_dir) / "cycling_bad_schandau.fit"
    shutil.copy(source_fit, fit_file)

    assert fit_file.is_file()

    fit_collector = FitCollector(garmin, target)
    fit_collector.copy_fit_files()

    # verify fit file got copied
    assert (target / "garmin" / "test_fit.FIT").is_file()
