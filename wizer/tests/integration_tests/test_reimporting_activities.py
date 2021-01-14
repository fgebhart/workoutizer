import datetime

from wizer import models
from wizer import configuration
from wizer.file_importer import import_activity_files, prepare_import_of_demo_activities, reimport_activity_files


def test_reimport_of_activities(db, tracks_in_tmpdir, client):
    """
    Test reimporter in following steps:
    1. import demo activities
    2. modify some attributes of a given activity
    3. remove demo activity flag, because demo activity won't get updated by reimporting
    4. trigger reimporter
    5. check that attributes have been overwritten with the original values
    6. check that activity page is accessible
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

    import_activity_files(models, importing_demo_data=True)
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 11
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

    # check that min and max altitude got imported, related to bug fix
    assert hiking.trace_file.max_altitude is not None
    assert hiking.trace_file.min_altitude is not None

    hiking_best_sections = models.BestSection.objects.get(activity=hiking.pk, section_distance=1)
    orig_1km_start_index = hiking_best_sections.start_index
    orig_1km_velocity = hiking_best_sections.max_value

    # 2. modify some attributes of a given activity
    hiking.distance = 5_000.0
    hiking.duration = datetime.timedelta(hours=500)
    hiking.name = "some arbitrary hiking name"
    hiking.save()

    hiking_best_sections.start_index = 50_000_000
    hiking_best_sections.max_value = 999.999
    hiking_best_sections.save()

    cycling.distance = 9_000.0
    cycling.duration = datetime.timedelta(hours=900)
    cycling.name = "some arbitrary cycling name"
    cycling.save()

    # get lap values to verify reimporter handles updating of lap data correctly
    lap_data = models.Lap.objects.filter(trace=cycling.trace_file)
    orig_lap_speeds = [lap.speed for lap in lap_data]
    # modify lap speed
    for lap in lap_data:
        lap.speed = 123456.789
        lap.save()

    # verify it got changed
    assert [lap.speed for lap in models.Lap.objects.filter(trace=cycling.trace_file)] != orig_lap_speeds

    # delete all cycling best sections
    for best_section in cycling_best_sections:
        best_section.delete()

    assert len(models.BestSection.objects.filter(activity=cycling.pk)) == 0

    # 3. remove demo activity flag (because reimporter does not modify demo activities)
    all_activities = models.Activity.objects.all()
    for activity in all_activities:
        activity.is_demo_activity = False
        activity.save()

    # 4. trigger reimport to update values
    reimport_activity_files(models)

    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 11
    # 5. check that attributes have been overwritten with the original values
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

    # verify lap data is back to original speed values
    updated_lap_data = models.Lap.objects.filter(trace=cycling.trace_file)
    updated_lap_speeds = [lap.speed for lap in updated_lap_data]
    assert updated_lap_speeds == orig_lap_speeds

    # 6. verify that the activity pages are accessible after reimporting
    activities = all_activities
    for activity in activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200


def test_reimporting_of_best_sections(db, tracks_in_tmpdir, import_one_activity):
    # import one cycling activity
    import_one_activity("2020-08-29-13-04-37.fit")

    assert models.Activity.objects.count() == 1
    assert models.Settings.objects.count() == 1

    import_activity_files(models, importing_demo_data=False)
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 1

    activity = models.Activity.objects.get()
    bs = models.BestSection.objects.filter(activity=activity, section_type="fastest")

    # there should never be more best sections of type 'fastest' than configured possible fastest sections
    assert len(bs) <= len(configuration.fastest_sections)

    # store original values
    orig_start_indexes = [section.start_index for section in bs]
    orig_end_indexes = [section.end_index for section in bs]
    orig_max_values = [section.max_value for section in bs]
    orig_number_of_best_sections = len(bs)

    # modify values
    for section in bs:
        section.start_index = 10_000
        section.end_index = 20_000
        section.max_value = 33_333.3
        section.save()

    # verify that the data got changed
    changed_bs = models.BestSection.objects.filter(activity=activity, section_type="fastest")
    assert [section.start_index for section in changed_bs] != orig_start_indexes
    assert [section.end_index for section in changed_bs] != orig_end_indexes
    assert [section.max_value for section in changed_bs] != orig_max_values

    # also add another dummy best section which should be removed again by the reimport
    dummy_section = models.BestSection(
        activity=activity,
        section_type="fastest",
        section_distance=12345,
        start_index=42,
        end_index=84,
        max_value=999.999,
    )
    dummy_section.save()

    # verify number of sections has increased
    assert (
        len(models.BestSection.objects.filter(activity=activity, section_type="fastest"))
        == orig_number_of_best_sections + 1
    )

    # now trigger reimport to update modified values
    reimport_activity_files(models)

    # check that dummy section was deleted because it is not present in the configured fastest sections
    assert (
        len(models.BestSection.objects.filter(activity=activity, section_type="fastest")) == orig_number_of_best_sections
    )

    # verify that the modified values are back to their original values
    # verify that the data got changed
    updated_bs = models.BestSection.objects.filter(activity=activity, section_type="fastest")
    assert [section.start_index for section in updated_bs] == orig_start_indexes
    assert [section.end_index for section in updated_bs] == orig_end_indexes
    assert [section.max_value for section in updated_bs] == orig_max_values

    for section in updated_bs:
        assert section.section_distance in configuration.fastest_sections
