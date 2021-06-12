import datetime
import shutil
import json
from pathlib import Path

import pytz

from wkz import models
from wkz.demo import copy_demo_fit_files_to_track_dir
from wkz.file_importer import run_importer__dask
from wkz.best_sections.generic import activity_suitable_for_awards
from wkz.tools.utils import calc_md5
from workoutizer import settings as django_settings


def test_activity_data_in_db_after_import(import_one_activity):
    """
    This test corresponds to tests.unit_tests.file_helper.test_fit_parser.test__parse_records
    but checks the integration with the database and the django model fields.
    """

    assert models.Activity.objects.count() == 0
    import_one_activity("example.fit")
    assert models.Activity.objects.count() == 1

    a = models.Activity.objects.get()

    assert a.sport.slug == "unknown"
    assert a.distance == 5.84
    assert a.duration == datetime.timedelta(seconds=3164)
    assert a.date == datetime.datetime(2019, 9, 14, 15, 22, tzinfo=pytz.UTC)
    assert a.trace_file.avg_heart_rate == 130
    assert a.trace_file.avg_speed == 1.845
    assert a.trace_file.avg_cadence == 64
    assert a.trace_file.avg_temperature == 27
    assert a.trace_file.calories == 432
    assert a.trace_file.aerobic_training_effect == 2.7
    assert a.trace_file.anaerobic_training_effect == 0.3
    # check lengths of list attributes
    assert len(json.loads(a.trace_file.heart_rate_list)) == 1224
    assert len(json.loads(a.trace_file.altitude_list)) == 1224
    assert len(json.loads(a.trace_file.latitude_list)) == 1224
    assert len(json.loads(a.trace_file.longitude_list)) == 1224
    assert len(json.loads(a.trace_file.distance_list)) == 1224
    assert len(json.loads(a.trace_file.cadence_list)) == 1224
    assert len(json.loads(a.trace_file.temperature_list)) == 1224
    assert len(json.loads(a.trace_file.speed_list)) == 1224
    assert len(json.loads(a.trace_file.timestamps_list)) == 1224
    # sanity check to see if element in list attributes
    assert 1.605 in json.loads(a.trace_file.speed_list)
    assert 8.697221484035255 in json.loads(a.trace_file.longitude_list)
    assert 49.40601873211563 in json.loads(a.trace_file.latitude_list)
    assert 1.6 in json.loads(a.trace_file.distance_list)
    assert 248.9 in json.loads(a.trace_file.altitude_list)
    assert 99 in json.loads(a.trace_file.heart_rate_list)
    assert 61 in json.loads(a.trace_file.cadence_list)
    assert 31 in json.loads(a.trace_file.temperature_list)
    assert 1568467325.0 in json.loads(a.trace_file.timestamps_list)
    # check laps
    laps = models.Lap.objects.filter(trace=a.trace_file)
    assert len(laps) == 7
    lap = laps[3]
    assert lap.start_time == datetime.datetime(2019, 9, 14, 14, 56, 48, tzinfo=pytz.UTC)
    assert lap.end_time == datetime.datetime(2019, 9, 14, 15, 3, 23, tzinfo=pytz.UTC)
    assert lap.distance == 1000.0
    assert lap.start_lat == 49.39987546764315
    assert lap.start_long == 8.704907605424525
    assert lap.end_lat == 49.405560996383436
    assert lap.end_long == 8.702977923676373
    assert lap.trigger == "distance"
    assert lap.speed == 2.52
    assert lap.label is None
    # check total ascent/descent
    assert a.trace_file.total_ascent == 234
    assert a.trace_file.total_descent == 233


def test_import_of_demo_activities(import_demo_data, client):
    # verify activities got imported
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 19

    for activity in all_activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200

    swimming = models.Activity.objects.filter(sport__slug="swimming")
    assert len(swimming) == 9
    # verify that swimming activities are considered for awards
    for s in swimming:
        assert s.evaluates_for_awards is True

    jogging = models.Activity.objects.filter(sport__slug="jogging")
    assert len(jogging) == 4
    # verify that jogging activities are considered for awards
    for j in jogging:
        assert j.evaluates_for_awards is True

    cycling = models.Activity.objects.filter(sport__slug="cycling")
    assert len(cycling) == 3
    # verify that cycling activities are considered for awards
    for c in cycling:
        assert c.evaluates_for_awards is True

    hiking = models.Activity.objects.filter(sport__slug="hiking")
    assert len(hiking) == 3

    # verify that hiking activities are not considered for awards
    # the entire hiking sport is set to False
    sport = models.Sport.objects.get(slug="hiking")
    assert sport.evaluates_for_awards is False
    for h in hiking:
        # each individual activity is set to True
        assert h.evaluates_for_awards is True
        # and thus at the end the activity evaluates to False
        assert activity_suitable_for_awards(h) is False

    # verify that best sections got parsed and imported
    best_sections_cnt = models.BestSection.objects.count()
    assert best_sections_cnt > 20

    # number of best sections is the sum of fastest and climb sections
    fastest_sections_cnt = models.BestSection.objects.filter(kind="fastest").count()
    climb_sections_cnt = models.BestSection.objects.filter(kind="climb").count()
    assert best_sections_cnt == fastest_sections_cnt + climb_sections_cnt


def test_import_of_activities__not_evaluates_for_awards(import_one_activity):
    # insert default sport
    sport = models.default_sport()

    assert models.Sport.objects.count() == 1
    assert models.Settings.objects.count() == 1

    # get default sport
    sport = models.Sport.objects.get()
    assert sport.name == "unknown"
    assert sport.evaluates_for_awards is True

    # change flag to false
    sport.evaluates_for_awards = False
    sport.save()
    assert sport.evaluates_for_awards is False

    # now import activity and verify that best sections still got saved to the db
    assert models.Activity.objects.count() == 0
    import_one_activity("cycling_bad_schandau.fit")
    assert models.Activity.objects.count() == 1

    # get activity
    activity = models.Activity.objects.get()
    assert activity.sport.evaluates_for_awards is False
    assert activity.evaluates_for_awards is True
    assert activity_suitable_for_awards(activity) is False

    # best sections got saved
    assert models.BestSection.objects.filter(activity=activity).count() > 0


def test_import_of_activities__evaluates_for_awards(import_one_activity):
    # insert default sport
    sport = models.default_sport()

    assert models.Sport.objects.count() == 1
    assert models.Settings.objects.count() == 1

    # get default sport
    sport = models.Sport.objects.get()
    assert sport.name == "unknown"
    assert sport.evaluates_for_awards is True

    # now import activity and verify that some best sections got saved to the db
    assert models.Activity.objects.count() == 0
    import_one_activity("cycling_bad_schandau.fit")
    assert models.Activity.objects.count() == 1

    # get activity
    activity = models.Activity.objects.get()
    assert activity.sport.evaluates_for_awards is True
    assert activity.evaluates_for_awards is True
    assert activity_suitable_for_awards(activity) is True

    # some best sections got saved
    assert models.BestSection.objects.filter(activity=activity).count() > 0


def test__activity_evaluates_for_awards(insert_activity):
    # in case both activity and sport are suitable, function should also return True
    activity = insert_activity(name="dummy-1", evaluates_for_awards=True)
    assert activity.evaluates_for_awards is True
    assert activity.sport.evaluates_for_awards is True
    assert activity_suitable_for_awards(activity=activity) is True

    # in case only activity is not suitable, function should return False
    activity = insert_activity(name="dummy-2", evaluates_for_awards=False)
    assert activity.evaluates_for_awards is False
    assert activity.sport.evaluates_for_awards is True
    assert activity_suitable_for_awards(activity=activity) is False

    # in case only sport is not suitable, function should return False
    activity = insert_activity(name="dummy", evaluates_for_awards=True)
    assert activity.evaluates_for_awards is True
    sport = activity.sport
    sport.evaluates_for_awards = False
    sport.save()
    assert activity.sport.evaluates_for_awards is False
    assert activity_suitable_for_awards(activity=activity) is False

    # in case both sport and activity are not suitable, function should also return False
    activity = insert_activity(name="dummy", evaluates_for_awards=False)
    assert activity.evaluates_for_awards is False
    sport = activity.sport
    sport.evaluates_for_awards = False
    sport.save()
    assert activity.sport.evaluates_for_awards is False
    assert activity_suitable_for_awards(activity=activity) is False


def test_avoid_unique_constraint_error(tracks_in_tmpdir, transactional_db, caplog):
    settings = models.get_settings()
    copy_demo_fit_files_to_track_dir(
        source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
        targe_dir=settings.path_to_trace_dir,
        list_of_files_to_copy=["cycling_bad_schandau.fit"],
    )

    # create second file with same checksum but different name
    shutil.copy(
        Path(settings.path_to_trace_dir) / "cycling_bad_schandau.fit",
        Path(settings.path_to_trace_dir) / "cycling_bad_schandau2.fit",
    )

    # in rare situations this lead to a unique constraint sql error because
    # of md5sum already being present in db, check that this does not fail
    run_importer__dask(models)

    # check that file importer warns about two files having the same checksum
    assert "The following two files have the same checksum, you might want to remove one of them:" in caplog.text


def test_import_corrupted_fit_file(tracks_in_tmpdir, caplog):
    assert models.Activity.objects.count() == 0
    settings = models.get_settings()

    copy_demo_fit_files_to_track_dir(
        source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
        targe_dir=settings.path_to_trace_dir,
        list_of_files_to_copy=["cycling_bad_schandau.fit"],
    )

    # create a corrupted fit file
    fit = Path(settings.path_to_trace_dir) / "faulty.fit"
    content = "no valid fit file content"
    fit.write_text(content)
    assert fit.read_text() == content

    # importer should not fail
    run_importer__dask(models)

    # one fit file should have been imported
    assert models.Activity.objects.count() == 1

    # but also an error was logged, however the execution should not have failed
    assert "ERROR" in caplog.text
    assert "Failed to parse fit file" in caplog.text


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


def test_run_importer__warns_about_duplicate_files(db, demo_data_dir, tracks_in_tmpdir, caplog):
    assert models.Activity.objects.count() == 0
    settings = models.get_settings()

    # copy the same file two times into two different files (with same checksum)
    file_a = Path(settings.path_to_trace_dir) / "a.fit"
    file_b = Path(settings.path_to_trace_dir) / "b.fit"
    source_file = Path(demo_data_dir) / "cycling_bad_schandau.fit"
    shutil.copy(source_file, file_a)
    shutil.copy(source_file, file_b)

    assert calc_md5(file_a) == calc_md5(file_b)

    # now run file importer and verify that a proper warning is logged
    run_importer__dask(models)

    assert "WARNING" in caplog.text
    assert (
        f"The following two files have the same checksum, you might want to remove one of them:{file_b} and {file_a}"
        in caplog.text
    )
