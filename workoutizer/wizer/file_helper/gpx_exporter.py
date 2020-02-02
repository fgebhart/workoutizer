import json
import os
import datetime

from django.conf import settings

from wizer.tools.utils import sanitize, timestamp_format


gpx_header = """<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="Fabian Gebhart" version="1.1" xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
     xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
     xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">
"""


def _gpx_file(time, name, track_points):
    return f"""{gpx_header}
    <metadata>
        <time>{time.strftime(timestamp_format)}</time>
        <link href="https://gitlab.com/fgebhart/workoutizer">
            <text>Workoutizer</text>
        </link>
    </metadata>
    <trk>
        <name>{name}</name>
        <trkseg>
            {track_points}
        </trkseg>
    </trk>
</gpx>
"""


def _track_points(coordinates: list, timestamps: list):
    track_points = ""
    for c, ts in zip(coordinates, timestamps):
        point = f"""<trkpt lat="{c[1]}" lon="{c[0]}">
                <time>{ts}</time>
            </trkpt>
            """
        track_points += point
    return track_points


def _build_gpx(time, file_name, coordinates: list, timestamps: list):
    return _gpx_file(time=time, name=file_name, track_points=_track_points(coordinates, timestamps))


def _fill_list_of_timestamps(start: datetime.date, duration, length: int):
    list_of_timestamps = []
    one_step_of_time = duration / length
    for i in range(length):
        list_of_timestamps.append((start + one_step_of_time * i).strftime(timestamp_format))
    return list_of_timestamps


def save_activity_to_gpx_file(activity):
    file_name = f"{activity.date}_{sanitize(activity.name)}.gpx"
    path = os.path.join(settings.MEDIA_ROOT, file_name)
    coordinates = json.loads(activity.trace_file.coordinates)
    file_content = _build_gpx(
        time=activity.date,
        file_name=activity.name,
        coordinates=coordinates,
        timestamps=_fill_list_of_timestamps(start=activity.date, duration=activity.duration, length=len(coordinates))
    )
    with open(path, "w+") as f:
        f.write(file_content)

    return path
