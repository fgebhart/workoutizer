from wizer.models import Traces, Sport


def test_creation_of_file_name(db):
    trace = Traces(path_to_file="/some/dummy/path/to/file.gpx", md5sum='asdfasdf')
    trace.save()
    assert trace.file_name == 'file.gpx'


def test_slugify_of_sport_name(db):
    sport = Sport(name='Some Crazy Stuff', color='red', icon='Bike')
    sport.save()
    assert sport.slug == 'some-crazy-stuff'
