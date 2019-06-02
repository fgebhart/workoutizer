import logging
from math import cos, sin, atan2, sqrt, radians, degrees

import gpxpy
import gpxpy.gpx
from geojson import MultiLineString

log = logging.getLogger(__name__)


def center_geolocation(geolocations):
    """
    Provide a relatively accurate center lat, lon returned as a list pair, given
    a list of list pairs.
    ex: in: geolocations = ((lat1,lon1), (lat2,lon2),)
        out: (center_lat, center_lon)
    """
    x = 0
    y = 0
    z = 0

    for lon, lat in geolocations:
        lat = radians(float(lat))
        lon = radians(float(lon))
        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)

    x = float(x / len(geolocations))
    y = float(y / len(geolocations))
    z = float(z / len(geolocations))

    return degrees(atan2(y, x)), degrees(atan2(z, sqrt(x * x + y * y)))


def fill_dict(name, activity, color, opacity, width, geometry):
    filled_dict = {
        "type": "FeatureCollection",
        "name": "tracks",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {"type": "Feature", "properties": {"name": name,
                                               "gpx_style_line": f"<gpx_style:color>{color}</gpx_style:color>"
                                               f"<gpx_style:opacity>{opacity}</gpx_style:opacity>"
                                               f"<gpx_style:width>{width}</gpx_style:width>",
                                               "locus_activity": activity}, "geometry": geometry}]}
    return filled_dict


class GPXConverter:
    def __init__(self, path_to_gpx, activity, track_name=None, line_color="D700D7", line_opacity="0.59",
                 line_width="4.0"):
        self.path = path_to_gpx
        self.activity = activity
        self.color = line_color
        self.opacity = line_opacity
        self.width = line_width
        self.track_name = track_name
        self.gpx = None
        self.geojson_multilinestring = None
        self.geojson_dict = None
        self.track_params = None

        # run converter
        self.read_gpx_file()
        self.parse_points()
        self.insert_data_into_geojson_dict()

    def read_gpx_file(self):
        gpx_file = open(self.path, 'r')
        self.gpx = gpxpy.parse(gpx_file)

    def parse_points(self):
        list_of_points = []
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    list_of_points.append((point.longitude, point.latitude))
        center = center_geolocation(list_of_points)
        print(f"center points: {center}")
        self.track_params = TrackParameters(center)
        self.geojson_multilinestring = MultiLineString([list_of_points])

    def insert_data_into_geojson_dict(self):
        if self.track_name:
            track_name = self.track_name
        else:
            track_name = self.gpx.tracks[0].name
        self.geojson_dict = fill_dict(
            name=track_name,
            activity=self.activity,
            color=self.color,
            opacity=self.opacity,
            width=self.width,
            geometry=self.geojson_multilinestring,
        )

    def get_geojson(self):
        return self.geojson_dict


class TrackParameters:
    def __init__(self, center):
        self.center_lon = center[1]
        self.center_lat = center[0]


# gjson = GPXConverter(path_to_gpx='../../../../tracks/2019-05-30_13-31-01.gpx', activity="cycling")
# print(gjson.get_geojson())

