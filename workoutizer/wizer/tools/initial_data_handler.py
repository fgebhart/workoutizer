import os
import datetime
import logging

from jinja2 import Environment, FileSystemLoader
from workoutizer import settings
from wizer.tools.utils import timestamp_format

log = logging.getLogger(__name__)

sport_data = {
    'name': ['Hiking', 'Swimming', 'Cycling', 'Jogging', 'unknown'],
    'color': ['ForestGreen', 'Navy', 'Gold', 'DarkOrange', 'gray'],
    'icon': ['hiking', 'swimmer', 'bicycle', 'running', 'question-circle'],
    'slug': ['hiking', 'swimming', 'cycling', 'jogging', 'unknown'],
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
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
            datetime.datetime.now() - datetime.timedelta(days=3 * counter + 2),
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
        'calories': [571, 432, 620,
                     571, 432, 620,
                     571, 432, 620]
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
            calories=activity.get('calories')[i],
        )
    log.info(f"created initial activities")


def create_initial_trace_data_with_recent_time():
    for i, trace_file in enumerate(_get_all_initial_trace_files()):
        if not os.path.isfile(os.path.join(settings.TRACKS_DIR, trace_file)):
            _insert_current_date_into_gpx(
                gpx=trace_file,
                strf_timestamp=(datetime.datetime.now() - datetime.timedelta(days=3 * i + 1)).strftime(
                    timestamp_format))


def _insert_current_date_into_gpx(gpx, strf_timestamp: str):
    log.debug(f"inserting recent time {strf_timestamp} into {gpx}")
    env = Environment(loader=FileSystemLoader(settings.INITIAL_TRACE_DATA_DIR))
    template = env.get_template(gpx)
    output_from_parsed_template = template.render(time=strf_timestamp)

    # to save the results
    new_file = os.path.join(settings.TRACKS_DIR, os.path.basename(gpx))
    with open(new_file, "w") as fh:
        log.debug(f"saving {new_file}")
        fh.write(output_from_parsed_template)


def _get_all_initial_trace_files():
    trace_files = []
    for (dirpath, dirnames, filenames) in os.walk(settings.INITIAL_TRACE_DATA_DIR):
        trace_files.extend(filenames)
        break
    return trace_files
