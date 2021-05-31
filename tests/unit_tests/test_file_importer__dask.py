import shutil
import datetime
from pathlib import Path

from dask.delayed import Delayed

from wkz.tools.utils import calc_md5
from wkz.file_helper.parser import Parser
from wkz.file_importer__dask import (
    _parse_single_file,
    _parse_all_files,
    run_importer__dask,
)
from wkz import models


def test__parse_single_file(demo_data_dir, fit_file):
    path = Path(demo_data_dir) / fit_file
    payload = _parse_single_file(path, "foo", demo_data_dir)
    assert isinstance(payload, Parser)

    # check core values which should have been changed
    assert payload.path_to_file == str(path)
    assert payload.file_name is not None
    assert payload.date is not None
    assert payload.md5sum == "foo"
    assert payload.sport is not None
    assert payload.duration != datetime.timedelta(minutes=0)


def test__parse_all_files(demo_data_dir, fit_file, fit_file_a, tmpdir):
    md5sums_from_db = []

    # test empty dir
    tasks = _parse_all_files(tmpdir, md5sums_from_db)
    assert tasks == []

    # test dir with one file
    activity_file = Path(demo_data_dir) / fit_file
    shutil.copy2(activity_file, tmpdir)
    tasks = _parse_all_files(tmpdir, md5sums_from_db)
    assert len(tasks) == 1
    assert isinstance(tasks[0], Delayed)

    # test dir with one file which is in db already
    md5sums_from_db = [calc_md5(activity_file)]
    tasks = _parse_all_files(tmpdir, md5sums_from_db)
    assert tasks == []

    # test dir with two files where one is in db already
    activity_file_2 = Path(demo_data_dir, fit_file_a)
    shutil.copy2(activity_file_2, tmpdir)
    tasks = _parse_all_files(tmpdir, md5sums_from_db)
    assert len(tasks) == 1
    assert isinstance(tasks[0], Delayed)


def test_run_importer__single_file(db, demo_data_dir, tmpdir, fit_file):
    assert models.Activity.objects.count() == 0
    settings = models.get_settings()
    settings.path_to_trace_dir = tmpdir
    settings.save()

    # test on empty dir
    run_importer__dask(models)
    assert models.Activity.objects.count() == 0

    # test on dir with one file
    activity_file = Path(demo_data_dir) / fit_file
    shutil.copy2(activity_file, tmpdir)
    run_importer__dask(models)
    assert models.Activity.objects.count() == 1


def test_run_importer__three_files(db, demo_data_dir, tmpdir, fit_file, fit_file_a, fit_file_b):
    assert models.Activity.objects.count() == 0
    settings = models.get_settings()
    settings.path_to_trace_dir = tmpdir
    settings.save()

    # test on dir with one file
    activity_file_1 = Path(demo_data_dir) / fit_file
    shutil.copy2(activity_file_1, tmpdir)
    activity_file_2 = Path(demo_data_dir) / fit_file_a
    shutil.copy2(activity_file_2, tmpdir)
    activity_file_3 = Path(demo_data_dir) / fit_file_b
    shutil.copy2(activity_file_3, tmpdir)
    run_importer__dask(models)
    assert models.Activity.objects.count() == 3
