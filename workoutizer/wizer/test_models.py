from django.test import TestCase

from .models import Traces, Sport


class TracesModelTests(TestCase):

    def test_creation_of_file_name(self):
        trace = Traces(path_to_file="/some/dummy/path/to/file.gpx", md5sum='asdfasdf')
        trace.save()
        self.assertEqual(trace.file_name, 'file.gpx')


class SportModelTest(TestCase):

    def test_slugify_of_sport_name(self):
        sport = Sport(name='Some Crazy Stuff', color='red', icon='Bike')
        sport.save()
        self.assertEqual(sport.slug, 'some-crazy-stuff')
