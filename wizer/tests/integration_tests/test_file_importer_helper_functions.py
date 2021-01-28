from wizer.file_importer import _activity_suitable_for_best_sections


def test__activity_suitable_for_best_sections(insert_activity):
    # in case both activity and sport are suitable, function should also return True
    activity = insert_activity(name="dummy-1", suitable_for_best_sections=True)
    assert activity.suitable_for_best_sections is True
    assert activity.sport.suitable_for_best_sections is True
    assert _activity_suitable_for_best_sections(activity=activity) is True

    # in case only activity is not suitable, function should return False
    activity = insert_activity(name="dummy-2", suitable_for_best_sections=False)
    assert activity.suitable_for_best_sections is False
    assert activity.sport.suitable_for_best_sections is True
    assert _activity_suitable_for_best_sections(activity=activity) is False

    # in case only sport is not suitable, function should return False
    activity = insert_activity(name="dummy", suitable_for_best_sections=True)
    assert activity.suitable_for_best_sections is True
    sport = activity.sport
    sport.suitable_for_best_sections = False
    sport.save()
    assert activity.sport.suitable_for_best_sections is False
    assert _activity_suitable_for_best_sections(activity=activity) is False

    # in case both sport and activity are not suitable, function should also return False
    activity = insert_activity(name="dummy", suitable_for_best_sections=False)
    assert activity.suitable_for_best_sections is False
    sport = activity.sport
    sport.suitable_for_best_sections = False
    sport.save()
    assert activity.sport.suitable_for_best_sections is False
    assert _activity_suitable_for_best_sections(activity=activity) is False
