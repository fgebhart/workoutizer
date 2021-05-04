from wkz import models


def test_automatic_naming_of_activity__gpx_with_coordinates(import_one_activity):
    import_one_activity("example.gpx")

    activity = models.Activity.objects.get()
    assert activity.name == "Evening Jogging in Heidelberg"


def test_automatic_naming_of_activity__fit_with_coordinates(import_one_activity):
    import_one_activity("hike_with_coordinates_muggenbrunn.fit")

    activity = models.Activity.objects.get()
    assert activity.name == "Noon Hiking in Aftersteg"


def test_automatic_naming_of_activity__fit_no_coordinates(import_one_activity):
    import_one_activity("swim_no_coordinates.fit")

    activity = models.Activity.objects.get()
    assert activity.name == "Noon Swimming"
