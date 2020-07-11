from wizer import models


def test_traces__creation_of_file_name(db):
    trace = models.Traces(path_to_file="/some/dummy/path/to/file.gpx", md5sum='asdfasdf')
    trace.save()
    assert trace.file_name == 'file.gpx'


def test_sport__slugify_of_sport_name(db):
    sport = models.Sport(name='Some Crazy Stuff', color='red', icon='Bike')
    sport.save()
    assert sport.slug == 'some-crazy-stuff'


def test_activity__with_default_unknown_sport(db):
    name = 'My Activity 1'
    activity = models.Activity(name=name)
    activity.save()
    assert activity.name == name
    assert activity.sport.name == 'unknown'
    assert activity.sport.icon == 'question-circle'
    assert activity.sport.color == 'gray'
    assert activity.sport.pk == 1
    # add second activity to verify that the same unknown sport instance is used
    name = 'My Activity 2'
    activity = models.Activity(name=name)
    activity.save()
    assert activity.name == name
    assert activity.sport.pk == 1
