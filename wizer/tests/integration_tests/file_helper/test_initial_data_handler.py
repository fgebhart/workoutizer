import os
import datetime

import pytz

from wizer.models import Activity, Settings, Sport
from wizer.file_helper.initial_data_handler import (
    change_date_of_demo_activities,
    copy_demo_fit_files_to_track_dir,
    insert_custom_demo_activities,
    insert_settings_and_sports_to_model,
)
from workoutizer import settings


def test_insert_settings_and_sports_to_model(db):
    # assert that there are no settings
    assert Settings.objects.count() == 0

    # insert settings and sports
    insert_settings_and_sports_to_model(Settings, Sport)
    assert Settings.objects.count() == 1
    assert Settings.objects.get(pk=1).number_of_days == 30

    # check that at least one sport object is present
    assert Sport.objects.count() > 0


def test_copy_demo_fit_files_to_track_dir(test_data_dir, demo_data_dir):
    # copy demo data to tested data dir
    src = demo_data_dir
    target = os.path.join(test_data_dir, "tested_data")
    copy_demo_fit_files_to_track_dir(src, target)
    assert os.path.isfile(os.path.join(target, "hike_with_coordinates.fit"))


def test_change_date_of_demo_activities(db, sport):
    # add Activities to test the changed date
    activity_a = Activity(
        name="activity_a",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=True,
    )
    activity_a.save()
    activity_b = Activity(
        name="activity_b",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=True,
    )
    activity_b.save()
    activity_c = Activity(
        name="activity_c",
        sport=sport,
        date=datetime.datetime(2000, 1, 1, tzinfo=pytz.utc),
        duration=datetime.timedelta(hours=1),
        distance=10.0,
        is_demo_activity=False,  # no demo activity
    )
    activity_c.save()
    demo_activities = Activity.objects.all()
    change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)

    a = Activity.objects.get(name="activity_a")
    b = Activity.objects.get(name="activity_b")
    c = Activity.objects.get(name="activity_c")

    # the date of activity a and b will be shifted to today - 1 or today - 3
    assert datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).date() - datetime.timedelta(days=1) == a.date.date()
    assert datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).date() - datetime.timedelta(days=4) == b.date.date()

    # the date of c should not be shifted
    assert datetime.datetime(2000, 1, 1, tzinfo=pytz.utc) == c.date


def test_insert_custom_demo_activities(db):
    activities = Activity.objects.all()
    assert len(activities) == 0
    insert_custom_demo_activities(
        count=8,
        every_nth_day=4,
        activity_model=Activity,
        sport_model=Sport,
    )
    activities = Activity.objects.all()
    assert len(activities) == 8
