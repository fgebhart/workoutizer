import datetime
import logging
import os
import shutil
from dataclasses import dataclass
from distutils.dir_util import copy_tree
from types import ModuleType

import pytz
from django.db import models

from wkz.tools.style import Colors, Set1Palette
from workoutizer import settings as django_settings

log = logging.getLogger(__name__)


@dataclass
class Sport:
    name: str
    mapping_name: str
    color: str
    icon: str
    slug: str
    evaluates_for_awards: bool


jogging = Sport("Jogging", "jogging", Colors.demo_sport_colors.jogging, "running", "jogging", True)
cycling = Sport("Cycling", "cycling", Colors.demo_sport_colors.cycling, "bicycle", "cycling", True)
hiking = Sport("Hiking", "hiking", Colors.demo_sport_colors.hiking, "hiking", "hiking", False)
swimming = Sport("Swimming", "swimming", Colors.demo_sport_colors.swimming, "swimmer", "swimming", False)
workout = Sport("Workout", "workout", Set1Palette.violet, "dumbbell", "workout", False)
skating = Sport("Skating", "skating", Set1Palette.brown, "person-skating", "skating", True)


sport_name_mapping = {
    "running": jogging,
    "cycling": cycling,
    "walking": hiking,
    "swimming": swimming,
    "training": workout,
    "generic": skating,
}


def copy_demo_fit_files_to_track_dir(source_dir: str, targe_dir: str, list_of_files_to_copy: list = []):
    log.debug(f"copying demo activities from {source_dir} to {targe_dir}")
    if not list_of_files_to_copy:
        copy_tree(source_dir, targe_dir)
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
    sport = sport_model.objects.get_or_create(
        name=swimming.name, slug=swimming.slug, icon=swimming.icon, color=swimming.color
    )
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
