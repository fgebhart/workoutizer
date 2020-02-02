import json
import os

from django.conf import settings

from wizer.tools.utils import sanitize

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
        <time>{time}</time>
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


def _track_points(coordinates: list):
    track_points = ""
    for c in coordinates:
        point = f'<trkpt lat="{c[1]}" lon="{c[0]}"></trkpt>\n            '
        track_points += point
    return track_points


def _build_gpx(time, file_name, coordinates: list):
    return _gpx_file(time=time, name=file_name, track_points=_track_points(coordinates))


def save_activity_to_gpx_file(activity):
    file_name = f"{activity.date}_{sanitize(activity.name)}.gpx"
    path = os.path.join(settings.MEDIA_ROOT, file_name)
    file_content = _build_gpx(
        time=activity.date,
        file_name=activity.name,
        coordinates=json.loads(activity.trace_file.coordinates),
    )
    with open(path, "w+") as f:
        f.write(file_content)

    return path
