import os

from wizer.file_importer import _run_parser
from wizer import models


def test_automatic_naming_of_activity__gpx_with_coordinates(db, test_data_dir):
    path_to_trace = os.path.join(test_data_dir, "example.gpx")
    _run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Evening Jogging in Heidelberg"


def test_automatic_naming_of_activity__fit_with_coordinates(db, demo_data_dir):
    path_to_trace = os.path.join(demo_data_dir, "hike_with_coodrinates_muggenbrunn.fit")
    _run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Noon Hiking in Aftersteg"


def test_automatic_naming_of_activity__fit_no_coordinates(db, test_data_dir):
    path_to_trace = os.path.join(test_data_dir, "swim_no_coordinates.fit")
    _run_parser(models=models, trace_files=[path_to_trace], importing_demo_data=False)

    activity = models.Activity.objects.all()[0]
    assert activity.name == "Noon Swimming"
