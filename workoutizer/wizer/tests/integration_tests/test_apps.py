import os

from django.urls import reverse

from wizer.apps import map_sport_name, sport_naming_map


def test_map_sport_name():
    assert map_sport_name('running', sport_naming_map) == "Jogging"
    assert map_sport_name('Running', sport_naming_map) == "Jogging"
    assert map_sport_name('swim', sport_naming_map) == "Swimming"


# def test_initial_data_insertion(db, client):
    # TODO does run in main loop and thus blocks execution of test
    # os.system("python manage.py runserver")
    # response = client.get(reverse("settings"))
    # assert response.status_code == 200
    # response = client.get("/activity/1")
    # assert response.status_code == 200