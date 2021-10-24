from wkz import models


def test_map_sport(db, import_one_activity, fit_file, fit_file_a, fit_file_c, fit_file_f):
    # check that no sport exists
    assert models.Sport.objects.count() == 0
    assert models.Activity.objects.count() == 0

    # import an activity file which is labelled 'running' and should be mapped to 'Jogging'
    import_one_activity(fit_file)
    assert models.Activity.objects.count() == 1
    assert models.Sport.objects.count() == 1

    sport = models.Sport.objects.get()
    assert sport.name == "Jogging"
    assert sport.mapping_name == "jogging"

    # now modify the sport name and verify activity will still be mapped to it
    sport.name = "Running"
    sport.save()
    import_one_activity(fit_file_a)
    assert models.Activity.objects.count() == 2
    assert models.Activity.objects.filter(sport__name="Running").count() == 2
    assert models.Activity.objects.filter(sport__mapping_name="jogging").count() == 2

    # import an activity which mapped to hiking
    import_one_activity(fit_file_c)
    assert models.Activity.objects.count() == 3
    assert models.Sport.objects.count() == 2
    assert models.Activity.objects.filter(sport__name="Hiking").count() == 1

    # import an activity which mapped to cycling
    import_one_activity(fit_file_f)
    assert models.Activity.objects.count() == 4
    assert models.Sport.objects.count() == 3
    assert models.Activity.objects.filter(sport__name="Cycling").count() == 1
