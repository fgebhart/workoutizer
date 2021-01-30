from wizer import models
from wizer.file_importer import _activity_suitable_for_awards


def test_import_of_demo_activities(import_demo_data, client):
    # verify activities got imported
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 19

    for activity in all_activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200

    swimming = models.Activity.objects.filter(sport__slug="swimming")
    assert len(swimming) == 9

    jogging = models.Activity.objects.filter(sport__slug="jogging")
    assert len(jogging) == 4

    cycling = models.Activity.objects.filter(sport__slug="cycling")
    assert len(cycling) == 3

    hiking = models.Activity.objects.filter(sport__slug="hiking")
    assert len(hiking) == 3

    # verify that best sections got parsed and imported
    best_sections = models.BestSection.objects.all()
    assert len(best_sections) == 61

    fastest_sections = models.BestSection.objects.filter(section_type="fastest")
    assert len(fastest_sections) == 61


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

    # now import activity and verify that no best sections got saved to the db
    assert models.Activity.objects.count() == 0
    import_one_activity("2020-08-29-13-04-37.fit")
    assert models.Activity.objects.count() == 1

    # get activity
    activity = models.Activity.objects.get()
    assert activity.sport.evaluates_for_awards is False
    assert activity.evaluates_for_awards is True
    assert _activity_suitable_for_awards(activity) is False

    # no best sections got saved
    assert models.BestSection.objects.filter(activity=activity).count() == 0


def test_import_of_activities__evaluates_for_awards(import_one_activity, tracks_in_tmpdir):
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
    import_one_activity("2020-08-29-13-04-37.fit")
    assert models.Activity.objects.count() == 1

    # get activity
    activity = models.Activity.objects.get()
    assert activity.sport.evaluates_for_awards is True
    assert activity.evaluates_for_awards is True
    assert _activity_suitable_for_awards(activity) is True

    # some best sections got saved
    assert models.BestSection.objects.filter(activity=activity).count() > 0
