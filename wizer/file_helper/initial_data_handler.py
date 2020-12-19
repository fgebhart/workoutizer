import datetime
import shutil
import logging

import pytz
from django.db.models import QuerySet

from workoutizer import settings

log = logging.getLogger(__name__)


sport_data = {
    "name": ["Hiking", "Swimming", "Cycling", "Jogging"],
    "color": ["ForestGreen", "Navy", "Gold", "DarkOrange"],
    "icon": ["hiking", "swimmer", "bicycle", "running"],
    "slug": ["hiking", "swimming", "cycling", "jogging"],
}


def insert_settings_and_sports_to_model(settings_model, sport_model):
    settings_model.objects.get_or_create(pk=1, path_to_trace_dir=settings.TRACKS_DIR, number_of_days=30)
    for i in range(len(sport_data["name"])):
        sport_model.objects.get_or_create(
            name=sport_data.get("name")[i],
            color=sport_data.get("color")[i],
            icon=sport_data.get("icon")[i],
            slug=sport_data.get("slug")[i],
        )


def copy_demo_fit_files_to_track_dir(source_dir: str, targe_dir: str):
    shutil.copytree(source_dir, targe_dir, dirs_exist_ok=True)


def change_date_of_demo_activities(every_nth_day: int, activities: QuerySet):
    today = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    for i, activity in enumerate(activities.filter(is_demo_activity=True)):
        # have an activity each 3rd day
        activity.date = today - datetime.timedelta(days=i * every_nth_day + 1)
        activity.save()


def insert_custom_demo_activities(count: int, every_nth_day: int, activity_model, sport_model):
    today = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    sport = sport_model.objects.get_or_create(name="Swimming", slug="swimming", icon="swimmer", color="Navy")
    for i in range(count):
        activity = activity_model(
            name="Swimming",
            date=today - datetime.timedelta(days=i * every_nth_day + 2),
            sport=sport[0],
            distance=2.0,
            duration=datetime.timedelta(minutes=90),
            is_demo_activity=True,
            description="Swimming training in my awesome pool.",
        )
        activity.save()
