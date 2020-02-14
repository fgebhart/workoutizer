import logging
import json
import datetime

log = logging.getLogger(__name__)


def migrate_traces(source_model, target_model):
    log.debug(f"migrating models: {source_model} -> {target_model}")
    source = source_model.objects.all()
    log.debug(f"got source query set: {source}")
    for trace in source:
        geojson = trace.geojson
        log.debug(f"got geojson: {geojson}")
        geometry = geojson.replace("'", "\"")
        geometry = json.loads(geometry)['features'][0]['geometry']
        log.debug(f"got geometry: {geometry}")
        target = target_model(
            path_to_file=trace.path_to_file,
            file_name=trace.file_name,
            md5sum=trace.md5sum,
            center_lat=trace.center_lat,
            center_lon=trace.center_lon,
            zoom_level=trace.zoom_level,
            geometry=geometry,
        )
        target.save()


def migrate_duration(activities):
    for activity in activities:
        timedelta = datetime.timedelta(minutes=activity.duration_old)
        log.debug(f"timedelta: {timedelta}")
        activity.duration = timedelta
        activity.save()
        log.debug(
            f"modified activity: {activity.pk}, duration_old: {activity.duration_old}, duration: {activity.duration}")
