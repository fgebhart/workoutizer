from wizer.models import Activity, Sport, Settings
from wizer.apps import run_file_importer


def test_import_of_demo_activities_by_running_server(db):
    run_file_importer(forking=False)

    # verify activities got imported
    assert len(Sport.objects.all()) == 5
    assert len(Settings.objects.all()) == 1
    assert len(Activity.objects.all()) == 19
