from wizer import models


def test_traces__creation_of_file_name(db):
    trace = models.Traces(path_to_file="/some/dummy/path/to/file.gpx", md5sum='asdfasdf')
    trace.save()
    assert trace.file_name == 'file.gpx'


def test_sport__slugify_of_sport_name(db):
    sport = models.Sport(name='Some Crazy Stuff', color='red', icon='Bike')
    sport.save()
    assert sport.slug == 'some-crazy-stuff'
