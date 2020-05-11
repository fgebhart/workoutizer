import datetime

import pytest

from wizer.models import Settings, Sport, Activity


@pytest.fixture
def settings(db):
    settings = Settings(
        path_to_trace_dir="/home/pi/traces/",
        path_to_garmin_device="/home/pi/traces/",
        file_checker_interval=90,
        number_of_days=30,
        trace_width=1.0,
        trace_opacity=0.7,
        plotting_style="bar",
        reimporter_updates_all=False,
        delete_files_after_import=False,
    )
    settings.save()
    return settings


@pytest.fixture
def sport(db):
    sport = Sport(name='Some Crazy Stuff', color='red', icon='Bike')
    sport.save()
    return sport


@pytest.fixture
def activity(db, sport):
    activity = Activity(
        name='Running',
        sport=sport,
        date=datetime.date.today(),
        duration=datetime.timedelta(minutes=30),
        distance=5.2,
        description="some super sport",
    )
    activity.save()
    return activity
