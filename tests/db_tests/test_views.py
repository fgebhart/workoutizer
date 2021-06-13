import datetime

import pytz
import pytest
import numpy as np
from django.urls import reverse

from wkz import models
from wkz.views import get_flat_list_of_pks_of_activities_in_top_awards, get_summary_of_all_activities
from workoutizer import settings as django_settings


def test_help_view(db, client):
    response = client.get(reverse("help"))
    assert response.status_code == 200
    assert "Keyboard Navigation" in response.content.decode("UTF-8")


def test_dashboard_view(db, client):
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert "Add Activity" in response.content.decode("UTF-8")


def test_settings_view(db, client):
    response = client.get(reverse("settings"))
    assert response.status_code == 200
    assert "Settings" in response.content.decode("UTF-8")


def test_best_sections_view(db, client):
    response = client.get(reverse("awards"))
    assert response.status_code == 200
    assert "awards" in response.content.decode("UTF-8")


def test_activity_view__activity_present(db, client, settings, sport, activity):
    pk = models.Activity.objects.get().pk
    response = client.get(f"/activity/{pk}")
    assert response.status_code == 200


def test_activity_view__no_activity(db, client):
    with pytest.raises(models.Activity.DoesNotExist):
        client.get("/activity/1")


def test_get_flat_list_of_pks_of_activities_in_top_awards(db, import_demo_data):
    result_pks = get_flat_list_of_pks_of_activities_in_top_awards()
    assert len(result_pks) == 7
    assert len(np.unique(result_pks)) == 7


def test_get_summary_of_all_activities(insert_sport, db, insert_activity):
    today = datetime.datetime.now().replace(tzinfo=pytz.timezone(django_settings.TIME_ZONE))

    # without any activity
    expected = {
        "count": 0,
        "duration": datetime.timedelta(seconds=0),
        "distance": 0,
        "seven_days_trend": datetime.timedelta(seconds=0),
    }
    result = get_summary_of_all_activities()
    assert expected == result

    # insert one activity
    insert_activity(date=today - datetime.timedelta(days=3))
    expected = {
        "count": 1,
        "duration": datetime.timedelta(seconds=1800),
        "distance": 5,
        "seven_days_trend": datetime.timedelta(seconds=1800),
    }
    result = get_summary_of_all_activities()
    assert expected == result

    # insert another activity with duration != 1800 sec
    insert_activity(date=today - datetime.timedelta(days=6), duration=datetime.timedelta(hours=7))
    expected = {
        "count": 2,
        "duration": datetime.timedelta(seconds=27000),
        "distance": 10,
        "seven_days_trend": datetime.timedelta(seconds=27000),
    }
    result = get_summary_of_all_activities()
    assert expected == result

    # insert another activity which is 8 days old and thus excluded from the seven days trend
    insert_activity(date=today - datetime.timedelta(days=8), duration=datetime.timedelta(hours=1))
    expected = {
        "count": 3,
        "duration": datetime.timedelta(seconds=30600),
        "distance": 15,
        "seven_days_trend": datetime.timedelta(seconds=27000),  # stays the same
    }
    result = get_summary_of_all_activities()
    assert expected == result

    # insert activity of other sport
    sport = insert_sport(name="Jumping", icon="cat")
    insert_activity(date=today - datetime.timedelta(days=2), duration=datetime.timedelta(hours=0.1), sport=sport)
    # get summary for the original sport 'cycling' which should bring the same results
    result = get_summary_of_all_activities("cycling")
    assert expected == result

    # without filtering for the sport, we expect:
    expected = {
        "count": 4,
        "duration": datetime.timedelta(seconds=30960),
        "distance": 20,
        "seven_days_trend": datetime.timedelta(seconds=27360),
    }
    result = get_summary_of_all_activities()
    assert expected == result
