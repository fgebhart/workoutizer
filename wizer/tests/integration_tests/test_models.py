from wizer import models


def test_traces__creation_of_file_name(db):
    trace = models.Traces(path_to_file="/some/dummy/path/to/file.gpx", md5sum="asdfasdf")
    trace.save()
    assert trace.file_name == "file.gpx"


def test_sport__slugify_of_sport_name(db):
    sport = models.Sport(name="Some Crazy Stuff", color="red", icon="Bike")
    sport.save()
    assert sport.slug == "some-crazy-stuff"


def test_activity__with_default_unknown_sport(db):
    name = "My Activity 1"
    activity_1 = models.Activity(name=name)
    activity_1.save()
    assert activity_1.name == name
    assert activity_1.sport.name == "unknown"
    assert activity_1.sport.icon == "question-circle"
    assert activity_1.sport.color == "gray"
    # add second activity to verify that the same unknown sport instance is used
    name = "My Activity 2"
    activity_2 = models.Activity(name=name)
    activity_2.save()
    assert activity_2.name == name
    assert activity_2.sport == activity_1.sport
