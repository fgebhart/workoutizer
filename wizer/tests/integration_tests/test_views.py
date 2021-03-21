from django.urls import reverse
import pytest
import numpy as np

from wizer import models
from wizer import configuration
from wizer.views import get_flat_list_of_pks_of_activities_in_top_awards


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
    assert "Save" in response.content.decode("UTF-8")


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
    result_pks = get_flat_list_of_pks_of_activities_in_top_awards(configuration.rank_limit)
    assert len(result_pks) == 7
    assert len(np.unique(result_pks)) == 7
