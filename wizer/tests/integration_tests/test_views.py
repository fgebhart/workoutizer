from django.urls import reverse
import pytest

from wizer.models import Activity


def test_help_view(db, client):
    response = client.get(reverse('help'))
    assert response.status_code == 200
    assert "Keyboard Navigation" in response.content.decode('UTF-8')


def test_dashboard_view(db, client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert "Add Activity" in response.content.decode('UTF-8')


def test_settings_view(db, client):
    response = client.get(reverse('settings'))
    assert response.status_code == 200
    assert "Save" in response.content.decode('UTF-8')


def test_activity_view(db, client, settings, sport, activity):
    response = client.get("/activity/1")
    assert response.status_code == 200


def test_activity_view__no_activity(db, client):
    with pytest.raises(Activity.DoesNotExist):
        client.get("/activity/1")
