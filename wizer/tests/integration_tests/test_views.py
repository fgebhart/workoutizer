from django.urls import reverse
import pytest

from wizer import models


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
    assert "Your Awards" in response.content.decode("UTF-8")


def test_activity_view__activity_present(db, client, settings, sport, activity):
    pk = models.Activity.objects.get().pk
    response = client.get(f"/activity/{pk}")
    assert response.status_code == 200


def test_activity_view__no_activity(db, client):
    with pytest.raises(models.Activity.DoesNotExist):
        client.get("/activity/1")
