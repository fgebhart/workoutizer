import datetime

import pytz

from wizer import models
from wizer import configuration
from wizer.file_importer import (
    import_activity_files,
    prepare_import_of_demo_activities,
    reimport_activity_files,
)
from wizer.best_sections.fastest import _activity_suitable_for_awards


def test_reimport_of_activities(db, tracks_in_tmpdir, client):
    """
    Test reimporter in following steps:
    1. import demo activities
    2. modify some attributes of a given activity
    3. trigger reimporter
    4. check that attributes have been overwritten with the original values
    5. check that activity page is accessible
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
    orig_cycling_date = cycling.date

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
    new_date = datetime.datetime(1999, 1, 1, 19, 19, 19, tzinfo=pytz.utc)

    hiking.distance = 5_000.0
    hiking.duration = datetime.timedelta(hours=500)
    hiking.name = "some arbitrary hiking name"
    # remove the demo activity flag of hiking activity
    hiking.is_demo_activity = False
    hiking.date = new_date
    hiking.save()

    hiking_best_sections.start_index = 50_000_000
    hiking_best_sections.max_value = 999.999
    hiking_best_sections.save()

    cycling.distance = 9_000.0
    cycling.duration = datetime.timedelta(hours=900)
    cycling.name = "some arbitrary cycling name"
    cycling.date = new_date
    cycling.save()

    # verify that cycling is a demo activity
    assert cycling.is_demo_activity is True

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

    # 3. trigger reimport to update values
    reimport_activity_files(models)

    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 11
    # 4. check that attributes have been overwritten with the original values
    updated_hiking = models.Activity.objects.get(sport__slug="hiking")
    assert updated_hiking.distance == orig_hiking_distance
    assert updated_hiking.duration == orig_hiking_duration
    # names should not be overwritten
    assert updated_hiking.name != orig_hiking_name
    assert updated_hiking.name == "some arbitrary hiking name"
    # the date should be not stay at its new value because the hiking activity is not a demo activity it should rather
    # be updated back to its original value, but thats hardly possible since the date of demo activities is adjusted to
    # reflect the current time
    assert updated_hiking.date != new_date

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
    # the date of an demo activity should also not updated back to its original
    assert updated_cycling.date != orig_cycling_date
    assert updated_cycling.date == new_date
    # verify that cycling is still a demo activity
    assert updated_cycling.is_demo_activity is True

    # verify that all cycling best sections got reimported and created again
    assert len(models.BestSection.objects.filter(activity=cycling.pk)) == orig_number_of_cycling_best_sections

    # verify lap data is back to original speed values
    updated_lap_data = models.Lap.objects.filter(trace=cycling.trace_file)
    updated_lap_speeds = [lap.speed for lap in updated_lap_data]
    assert updated_lap_speeds == orig_lap_speeds

    # 5. verify that the activity pages are accessible after reimporting
    activities = all_activities
    for activity in activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200


def test_reimporting_of_best_sections(import_one_activity):
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


def test_reimport__not_evaluates_for_awards__changing_sport_flag(import_one_activity):
    # Changed behaviour of this test to check that best sections do not get removed when changing evaluates_for_awards

    import_one_activity("2020-08-29-13-04-37.fit")

    # verify activity is suitable for best sections
    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is True
    assert models.BestSection.objects.filter(activity=activity).count() > 0

    # change sport flag for evaluates_for_awards to False
    sport = activity.sport
    sport.evaluates_for_awards = False
    sport.save()
    assert _activity_suitable_for_awards(activity) is False

    # reimport activity
    reimport_activity_files(models)

    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is False

    # check that best sections did not get removed
    assert models.BestSection.objects.filter(activity=activity).count() > 0

    # now change everything back and verify that the best sections get saved to db again by reimporting
    sport = activity.sport
    sport.evaluates_for_awards = True
    sport.save()
    assert _activity_suitable_for_awards(activity) is True

    # reimport activity
    reimport_activity_files(models)

    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is True

    # check that best sections got removed
    assert models.BestSection.objects.filter(activity=activity).count() > 0


def test_reimport__not_evaluates_for_awards__changing_activity_flag(import_one_activity):
    # Changed behaviour of this test to check that best sections do not get removed when changing evaluates_for_awards

    import_one_activity("2020-08-29-13-04-37.fit")

    # verify activity is suitable for best sections
    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is True
    assert models.BestSection.objects.filter(activity=activity).count() > 0

    # change activity flag for evaluates_for_awards to False
    activity.evaluates_for_awards = False
    activity.save()
    assert _activity_suitable_for_awards(activity) is False

    # reimport activity
    reimport_activity_files(models)

    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is False

    # check that best sections did not get removed
    assert models.BestSection.objects.filter(activity=activity).count() > 0

    # now change everything back and verify that the best sections get saved to db again by reimporting
    activity.evaluates_for_awards = True
    activity.save()
    assert _activity_suitable_for_awards(activity) is True

    # reimport activity
    reimport_activity_files(models)

    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert _activity_suitable_for_awards(activity) is True

    # check that best sections got removed
    assert models.BestSection.objects.filter(activity=activity).count() > 0
