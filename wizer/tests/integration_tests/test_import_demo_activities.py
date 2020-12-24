from wizer import models
from wizer.file_importer import run_file_importer, prepare_import_of_demo_activities


def test_import_of_demo_activities(db, tracks_in_tmpdir):

    prepare_import_of_demo_activities(models)
    assert len(models.Sport.objects.all()) == 5
    assert len(models.Settings.objects.all()) == 1

    run_file_importer(models, importing_demo_data=True)
    # verify activities got imported
    assert len(models.Activity.objects.all()) == 19

    swimming = models.Activity.objects.filter(sport__slug="swimming")
    assert len(swimming) == 9

    jogging = models.Activity.objects.filter(sport__slug="jogging")
    assert len(jogging) == 4

    cycling = models.Activity.objects.filter(sport__slug="cycling")
    assert len(cycling) == 3

    hiking = models.Activity.objects.filter(sport__slug="hiking")
    assert len(hiking) == 3
