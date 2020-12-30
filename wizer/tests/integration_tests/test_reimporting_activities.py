import datetime

from wizer import models
from wizer.file_importer import FileImporter, prepare_import_of_demo_activities
from wizer.file_helper.reimporter import Reimporter


def test_reimport_of_activities(db, tracks_in_tmpdir):
    """
    Test reimporter in following steps:
    1. import demo activities
    2. modify some attributes of a given activity
    3. trigger reimporter
    4. check that attributes have been overwritten with the original values
    """

    # 1. import one cycling and one hiking activities
    prepare_import_of_demo_activities(
        models,
        list_of_files_to_copy=[
            "hike_with_coordinates.fit",
            "2020-08-29-13-04-37.fit",
        ],
    )
    assert len(models.Sport.objects.all()) == 5
    assert len(models.Settings.objects.all()) == 1

    FileImporter(models, importing_demo_data=True)
    assert len(models.Activity.objects.all()) == 11
    assert len(models.Activity.objects.filter(sport__slug="swimming")) == 9
    assert len(models.Activity.objects.filter(sport__slug="jogging")) == 0

    all_cycling = models.Activity.objects.filter(sport__slug="cycling")
    assert len(all_cycling) == 1
    cycling = all_cycling[0]
    orig_cycling_distance = cycling.distance
    orig_cycling_duration = cycling.duration
    orig_cycling_name = cycling.name

    cycling_best_sections = models.BestSection.objects.filter(activity=cycling.pk)
    orig_number_of_cycling_best_sections = len(cycling_best_sections)

    all_hiking = models.Activity.objects.filter(sport__slug="hiking")
    assert len(all_hiking) == 1
    hiking = all_hiking[0]
    orig_hiking_distance = hiking.distance
    orig_hiking_duration = hiking.duration
    orig_hiking_name = hiking.name

    hiking_best_sections = models.BestSection.objects.get(activity=hiking.pk, section_distance=1)
    orig_1km_start_index = hiking_best_sections.start_index
    orig_1km_velocity = hiking_best_sections.max_value

    # 2. modify some attributes of a given activity
    hiking.distance = 5000.0
    hiking.duration = datetime.timedelta(hours=500)
    hiking.name = "some arbitrary hiking name"
    hiking.save()

    hiking_best_sections.start_index = 50_000_000
    hiking_best_sections.max_value = 999.999
    hiking_best_sections.save()

    cycling.distance = 9000.0
    cycling.duration = datetime.timedelta(hours=900)
    cycling.name = "some arbitrary cycling name"
    cycling.save()

    # delete all cycling best sections
    for best_section in cycling_best_sections:
        best_section.delete()

    assert len(models.BestSection.objects.filter(activity=cycling.pk)) == 0

    # 3. trigger reimporter to update values
    Reimporter()

    # 4. check that attributes have been overwritten with the original values
    updated_hiking = models.Activity.objects.get(sport__slug="hiking")
    assert updated_hiking.distance == orig_hiking_distance
    assert updated_hiking.duration == orig_hiking_duration
    # names should not be overwritten
    assert updated_hiking.name != orig_hiking_name
    assert updated_hiking.name == "some arbitrary hiking name"

    # verify that attributes of best section got overwritten
    updated_hiking_best_sections = models.BestSection.objects.get(activity=updated_hiking.pk, section_distance=1)
    assert updated_hiking_best_sections.start_index == orig_1km_start_index
    assert updated_hiking_best_sections.max_value == orig_1km_velocity

    updated_cycling = models.Activity.objects.get(sport__slug="cycling")
    assert updated_cycling.distance == orig_cycling_distance
    assert updated_cycling.duration == orig_cycling_duration
    # names should not be overwritten
    assert updated_cycling.name != orig_cycling_name
    assert updated_cycling.name == "some arbitrary cycling name"

    # verify that all cycling best sections got reimported and created again
    assert len(models.BestSection.objects.filter(activity=cycling.pk)) == orig_number_of_cycling_best_sections
