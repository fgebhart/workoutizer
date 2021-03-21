from wizer import models
from wizer.best_sections.generic import _activity_suitable_for_awards


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
        assert _activity_suitable_for_awards(h) is False

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
    assert _activity_suitable_for_awards(activity) is False

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
    assert _activity_suitable_for_awards(activity) is True

    # some best sections got saved
    assert models.BestSection.objects.filter(activity=activity).count() > 0


def test__activity_evaluates_for_awards(insert_activity):
    # in case both activity and sport are suitable, function should also return True
    activity = insert_activity(name="dummy-1", evaluates_for_awards=True)
    assert activity.evaluates_for_awards is True
    assert activity.sport.evaluates_for_awards is True
    assert _activity_suitable_for_awards(activity=activity) is True

    # in case only activity is not suitable, function should return False
    activity = insert_activity(name="dummy-2", evaluates_for_awards=False)
    assert activity.evaluates_for_awards is False
    assert activity.sport.evaluates_for_awards is True
    assert _activity_suitable_for_awards(activity=activity) is False

    # in case only sport is not suitable, function should return False
    activity = insert_activity(name="dummy", evaluates_for_awards=True)
    assert activity.evaluates_for_awards is True
    sport = activity.sport
    sport.evaluates_for_awards = False
    sport.save()
    assert activity.sport.evaluates_for_awards is False
    assert _activity_suitable_for_awards(activity=activity) is False

    # in case both sport and activity are not suitable, function should also return False
    activity = insert_activity(name="dummy", evaluates_for_awards=False)
    assert activity.evaluates_for_awards is False
    sport = activity.sport
    sport.evaluates_for_awards = False
    sport.save()
    assert activity.sport.evaluates_for_awards is False
    assert _activity_suitable_for_awards(activity=activity) is False
