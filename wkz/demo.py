import datetime
import shutil
import logging
import os

import pytz
from django.db import models
from types import ModuleType

from workoutizer import settings as django_settings

log = logging.getLogger(__name__)


sport_data = {
    "name": ["Hiking", "Swimming", "Cycling", "Jogging"],
    "color": ["#6BD098", "#51CBCE", "#FCC468", "#F17E5D"],
    "icon": ["hiking", "swimmer", "bicycle", "running"],
    "slug": ["hiking", "swimming", "cycling", "jogging"],
    "evaluates_for_awards": [False, True, True, True],
}


def insert_demo_sports_to_model(models):
    # also insert default unknown sport
    models.default_sport()
    for i in range(len(sport_data["name"])):
        models.Sport.objects.get_or_create(
            name=sport_data.get("name")[i],
            color=sport_data.get("color")[i],
            icon=sport_data.get("icon")[i],
            slug=sport_data.get("slug")[i],
            evaluates_for_awards=sport_data.get("evaluates_for_awards")[i],
        )


def copy_demo_fit_files_to_track_dir(source_dir: str, targe_dir: str, list_of_files_to_copy: list = []):
    log.debug(f"copying demo activities from {source_dir} to {targe_dir}")
    if not list_of_files_to_copy:
        shutil.copytree(source_dir, targe_dir, dirs_exist_ok=True)
    else:
        for file in list_of_files_to_copy:
            shutil.copy2(os.path.join(source_dir, file), targe_dir)


def change_date_of_demo_activities(every_nth_day: int, activities: models.QuerySet):
    today = datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE))
    for i, activity in enumerate(activities.filter(is_demo_activity=True)):
        # have an activity each 3rd day
        activity.date = today - datetime.timedelta(days=i * every_nth_day + 1)
        activity.save()


def insert_custom_demo_activities(count: int, every_nth_day: int, activity_model, sport_model):
    today = datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE))
    sport = sport_model.objects.get_or_create(name="Swimming", slug="swimming", icon="swimmer", color="#51CBCE")
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


def prepare_import_of_demo_activities(models, list_of_files_to_copy: list = []):
    settings = models.get_settings()
    insert_demo_sports_to_model(models)
    copy_demo_fit_files_to_track_dir(
        source_dir=django_settings.INITIAL_TRACE_DATA_DIR,
        targe_dir=settings.path_to_trace_dir,
        list_of_files_to_copy=list_of_files_to_copy,
    )


def finalize_demo_activity_insertion(models: ModuleType) -> None:
    demo_activities = models.Activity.objects.filter(is_demo_activity=True)
    change_date_of_demo_activities(every_nth_day=3, activities=demo_activities)
    insert_custom_demo_activities(count=9, every_nth_day=3, activity_model=models.Activity, sport_model=models.Sport)
    log.info("finished inserting demo data")
