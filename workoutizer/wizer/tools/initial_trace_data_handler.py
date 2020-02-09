import os
import datetime
import logging

from jinja2 import Environment, FileSystemLoader
from workoutizer import settings
from wizer.tools.utils import timestamp_format

log = logging.getLogger(__name__)


def insert_settings_and_sports_to_model(settings_model, sport_model):
    settings_model.objects.get_or_create(path_to_trace_dir=settings.TRACKS_DIR, number_of_days=10)
    sport_model.objects.get_or_create(name='Hiking', color='FireBrick', icon='hiking', slug='hiking')
    sport_model.objects.get_or_create(name='Swimming', color='LightSeaGreen', icon='swimmer', slug='swimming')
    sport_model.objects.get_or_create(name='Cycling', color='Gold', icon='bicycle', slug='cycling')
    sport_model.objects.get_or_create(name='Workout', color='Lime', icon='dumbbell', slug='workout')


def create_initial_trace_data_with_recent_time():
    for i, trace_file in enumerate(_get_all_initial_trace_files()):
        if not os.path.isfile(os.path.join(settings.TRACKS_DIR, trace_file)):
            _insert_current_date_into_gpx(
                gpx=trace_file,
                strf_timestamp=(datetime.datetime.now() - datetime.timedelta(days=i)).strftime(timestamp_format))


def _insert_current_date_into_gpx(gpx, strf_timestamp: str):
    log.debug(f"inserting recent time {strf_timestamp} into {gpx}")
    env = Environment(loader=FileSystemLoader(settings.INITIAL_TRACE_DATA_DIR))
    template = env.get_template(gpx)
    output_from_parsed_template = template.render(time=strf_timestamp)

    # to save the results
    with open(os.path.join(settings.TRACKS_DIR, os.path.basename(gpx)), "w") as fh:
        fh.write(output_from_parsed_template)


def _get_all_initial_trace_files():
    trace_files = []
    for (dirpath, dirnames, filenames) in os.walk(settings.INITIAL_TRACE_DATA_DIR):
        trace_files.extend(filenames)
        break
    return trace_files
