import os
import datetime
import logging

import pytz
from jinja2 import Environment, FileSystemLoader
from workoutizer import settings
from wizer.tools.utils import timestamp_format

log = logging.getLogger(__name__)

sport_data = {
    'name': ['Hiking', 'Swimming', 'Cycling', 'Jogging'],
    'color': ['ForestGreen', 'Navy', 'Gold', 'DarkOrange'],
    'icon': ['hiking', 'swimmer', 'bicycle', 'running'],
    'slug': ['hiking', 'swimming', 'cycling', 'jogging'],
}


def _activity_data(sport_model, counter):
    return {
        'name': [
            'Indoor Club Training', 'Cycling on Hometrainer', 'Indoor Club Training',
            'Indoor Club Training', 'Cycling on Hometrainer', 'Indoor Club Training',
            'Indoor Club Training', 'Cycling on Hometrainer', 'Indoor Club Training',
        ],
        'sport': [
            sport_model.objects.get(name='Swimming'),
            sport_model.objects.get(name='Cycling'),
            sport_model.objects.get(name='Swimming'),
            sport_model.objects.get(name='Swimming'),
            sport_model.objects.get(name='Cycling'),
            sport_model.objects.get(name='Swimming'),
            sport_model.objects.get(name='Swimming'),
            sport_model.objects.get(name='Cycling'),
            sport_model.objects.get(name='Swimming'),
        ],
        'date': [
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
            pytz.utc.localize(datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2)),
        ],
        'duration': [
            datetime.timedelta(minutes=90),
            datetime.timedelta(minutes=48),
            datetime.timedelta(minutes=82),
            datetime.timedelta(minutes=90),
            datetime.timedelta(minutes=48),
            datetime.timedelta(minutes=82),
            datetime.timedelta(minutes=90),
            datetime.timedelta(minutes=48),
            datetime.timedelta(minutes=82),
        ],
    }


def insert_settings_and_sports_to_model(settings_model, sport_model):
    settings_model.objects.get_or_create(pk=1, path_to_trace_dir=settings.TRACKS_DIR, number_of_days=30)
    log.info(f"created initial settings")
    for i in range(len(sport_data['name'])):
        sport_model.objects.get_or_create(
            name=sport_data.get('name')[i],
            color=sport_data.get('color')[i],
            icon=sport_data.get('icon')[i],
            slug=sport_data.get('slug')[i])
    log.info(f"created initial sports")


def insert_activities_to_model(sport_model, activity_model):
    for i in range(len(_activity_data(sport_model, 2)['name'])):
        activity = _activity_data(sport_model, i)
        activity_model.objects.get_or_create(
            name=activity.get('name')[i],
            sport=activity.get('sport')[i],
            date=activity.get('date')[i],
            duration=activity.get('duration')[i],
            is_demo_activity=True,
        )
    log.info(f"created initial activities")


def create_demo_trace_data_with_recent_time():
    for i, trace_file in enumerate(_get_all_initial_trace_files()):
        if not os.path.isfile(os.path.join(settings.TRACKS_DIR, trace_file)):
            _insert_current_date_into_gpx(
                gpx_file_name=trace_file,
                source_path=settings.INITIAL_TRACE_DATA_DIR,
                target_path=settings.TRACKS_DIR,
                strf_timestamp=(datetime.datetime.now() - datetime.timedelta(days=3 * i + 1)).strftime(
                    timestamp_format))


def _insert_current_date_into_gpx(gpx_file_name: str, source_path: str, target_path: str, strf_timestamp: str):
    log.debug(f"inserting recent time {strf_timestamp} into {gpx_file_name}")
    env = Environment(loader=FileSystemLoader(source_path))
    template = env.get_template(gpx_file_name)
    output_from_parsed_template = template.render(time=strf_timestamp)

    # to save the results
    new_file = os.path.join(target_path, os.path.basename(gpx_file_name))
    with open(new_file, "w") as fh:
        log.debug(f"saving {new_file}")
        fh.write(output_from_parsed_template)


def _get_all_initial_trace_files():
    trace_files = []
    for (dirpath, dirnames, filenames) in os.walk(settings.INITIAL_TRACE_DATA_DIR):
        trace_files.extend(filenames)
        break
    return trace_files
