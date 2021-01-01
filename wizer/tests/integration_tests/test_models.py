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


def test_best_section__always_add_top_one(db, insert_best_section):
    insert_best_section(max_value=1.0)
    section = models.BestSection.objects.get()
    assert section.section_type == "fastest"
    assert section.max_value == 1.0

    # verify that the above added best section is in top scores rank 1
    top_scores = models.BestSectionTopScores.objects.all()
    assert len(top_scores) == 1
    assert top_scores[0].section.max_value == 1.0

    # insert another best section with even higher max value
    insert_best_section(max_value=2.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 2
    assert top_scores[0].section.max_value == 2.0
    assert top_scores[1].section.max_value == 1.0

    # insert another best section with even higher max value
    insert_best_section(max_value=3.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 3.0
    assert top_scores[1].section.max_value == 2.0
    assert top_scores[2].section.max_value == 1.0

    # insert another new best score which should be position 1 and the lowest should be dropped
    insert_best_section(max_value=4.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 4.0
    assert top_scores[1].section.max_value == 3.0
    assert top_scores[2].section.max_value == 2.0

    # insert another section with lower max value which should not end up in top scores
    insert_best_section(max_value=0.5)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 4.0
    assert top_scores[1].section.max_value == 3.0
    assert top_scores[2].section.max_value == 2.0


def test_best_section__also_add_from_behind(db, insert_best_section):
    insert_best_section(max_value=5.0)

    top_scores = models.BestSectionTopScores.objects.all()
    assert len(top_scores) == 1
    assert top_scores[0].section.max_value == 5.0

    # insert new section which would be rank 2
    insert_best_section(max_value=4.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 2
    assert top_scores[0].section.max_value == 5.0
    assert top_scores[1].section.max_value == 4.0

    # insert another new section which would be rank 3
    insert_best_section(max_value=3.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 5.0
    assert top_scores[1].section.max_value == 4.0
    assert top_scores[2].section.max_value == 3.0

    # insert another new section which would be rank 4, but rank 4 should not be stored to db
    insert_best_section(max_value=2.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 5.0
    assert top_scores[1].section.max_value == 4.0
    assert top_scores[2].section.max_value == 3.0

    # insert new section with exactly the same max value as rank 2 to verify rank 2 and 3 are equal
    insert_best_section(max_value=4.0)
    top_scores = models.BestSectionTopScores.objects.all().order_by("rank")
    assert len(top_scores) == 3
    assert top_scores[0].section.max_value == 5.0
    assert top_scores[1].section.max_value == 4.0
    assert top_scores[2].section.max_value == 4.0
