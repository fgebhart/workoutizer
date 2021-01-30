from wizer.file_importer import _activity_suitable_for_awards


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
