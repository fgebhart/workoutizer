import os
import datetime

import pytz

from wkz import models
from wkz.demo import (
    change_date_of_demo_activities,
    copy_demo_fit_files_to_track_dir,
    insert_custom_demo_activities,
    insert_demo_sports_to_model,
)
from workoutizer import settings as django_settings


def test_insert_demo_sports_to_model(db, flush_db):
    # assert that there are no sports
    assert models.Sport.objects.count() == 0
    # insert sports
    insert_demo_sports_to_model(models)
    # check that all sports are created
    assert models.Sport.objects.count() == 5


def test_copy_demo_fit_files_to_track_dir__all(tmpdir, demo_data_dir):
    # copy demo data to tested data dir
    src = demo_data_dir
    copy_demo_fit_files_to_track_dir(src, tmpdir, list_of_files_to_copy=[])
    assert os.path.isfile(os.path.join(tmpdir, "hike_with_coordinates_muggenbrunn.fit"))
    number_of_files_in_dir = len([name for name in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, name))])
    assert number_of_files_in_dir == 10


def test_copy_demo_fit_files_to_track_dir__not_all(tmpdir, demo_data_dir):
    # copy demo data to tested data dir
    src = demo_data_dir
    copy_demo_fit_files_to_track_dir(
        src,
        tmpdir,
        list_of_files_to_copy=[
            "hike_with_coordinates_muggenbrunn.fit",
            "2020-08-20-09-34-33.fit",
        ],
    )
    assert os.path.isfile(os.path.join(tmpdir, "hike_with_coordinates_muggenbrunn.fit"))
    assert os.path.isfile(os.path.join(tmpdir, "2020-08-20-09-34-33.fit"))
    number_of_files_in_dir = len([name for name in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, name))])
    assert number_of_files_in_dir == 2


def test_change_date_of_demo_activities(db, sport):
    # add Activities to test the changed date
    activity_a = models.Activity(
        name="activity_a",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=True,
    )
    activity_a.save()
    activity_b = models.Activity(
        name="activity_b",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=True,
    )
    activity_b.save()
    activity_c = models.Activity(
        name="activity_c",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=False,  # no demo activity
    )
    activity_c.save()
    demo_activities = models.Activity.objects.all()
    change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)

    a = models.Activity.objects.get(name="activity_a")
    b = models.Activity.objects.get(name="activity_b")
    c = models.Activity.objects.get(name="activity_c")

    # the date of activity a and b will be shifted to today - 1 or today - 3
    assert (
        datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE)).date() - datetime.timedelta(days=1)
        == a.date.date()
    )
    assert (
        datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE)).date() - datetime.timedelta(days=4)
        == b.date.date()
    )

    # the date of c should not be shifted
    assert datetime.datetime(2000, 1, 1, tzinfo=pytz.utc) == c.date


def test_insert_custom_demo_activities(db):
    activities = models.Activity.objects.all()
    assert len(activities) == 0
    insert_custom_demo_activities(
        count=8,
        every_nth_day=4,
        activity_model=models.Activity,
        sport_model=models.Sport,
    )
    activities = models.Activity.objects.all()
    assert len(activities) == 8
