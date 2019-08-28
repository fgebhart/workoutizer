import logging
from dataclasses import dataclass
from math import cos, sin, atan2, sqrt, radians, degrees

from geopy import distance
import gpxpy
import gpxpy.gpx
from geojson import MultiLineString


log = logging.getLogger('wizer.gpx-converter')


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
    def __init__(self, path_to_gpx, track_name=None, line_color="#ff0000", line_opacity="0.59",
                 line_width="4.0"):
        self.path = path_to_gpx
        self.color = line_color
        self.opacity = line_opacity
        self.width = line_width
        self.track_name = track_name
        self.sport = None
        self.duration = None
        self.distance = None
        self.date = None
        self.gpx = None
        self.geojson_multilinestring = None
        self.center = None
        self.geojson_dict = None
        # self.root = None

        # run converter
        try:
            self.read_gpx_file()
            self.parse_points()
            self.insert_data_into_geojson_dict()
        except Exception as e:
            log.error(f"could not import file: {self.path}\n"
                      f"got error: {e}", exc_info=True)

    def read_gpx_file(self):
        gpx_file = open(self.path, 'r')
        self.gpx = gpxpy.parse(gpx_file)
        self.get_sport_from_gpx_file()
        self.get_duration_from_gpx_file()

    def get_sport_from_gpx_file(self):
        for e in self.gpx.tracks[0].extensions:
            if e.tag.split("}")[1] == "activity":
                self.sport = e.text
                log.debug(f"found sport: {self.sport}")

    def get_duration_from_gpx_file(self):
        all_points_time = []
        for s in self.gpx.tracks[0].segments:
            for p in s.points:
                all_points_time.append(p.time)
        start = all_points_time[0]
        self.date = start
        end = all_points_time[-1]
        self.duration = convert_timedelta_to_hours(end - start)
        log.debug(f"found duration: {self.duration}")

    def parse_points(self):
        list_of_points = []
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    list_of_points.append((point.longitude, point.latitude))
        self.center = center_geolocation(list_of_points)
        # log.debug(f"center points: {self.center}")
        self.geojson_multilinestring = MultiLineString([list_of_points])
        self.distance = calc_distance_of_points(list_of_points)
        log.debug(f"found distance: {self.distance}")

    def insert_data_into_geojson_dict(self):
        if self.track_name:
            track_name = self.track_name
        else:
            track_name = self.gpx.tracks[0].name
        self.geojson_dict = fill_dict(
            name=track_name,
            activity=self.sport,
            color=self.color,
            opacity=self.opacity,
            width=self.width,
            geometry=self.geojson_multilinestring,
        )

    def get_gpx_metadata(self):
        return GPXFileMetadata(
            title=self.path.split(".gpx")[0].split("/")[-1],
            sport=self.sport,
            date=self.date,
            duration=self.duration,
            center_lon=self.center[1],
            center_lat=self.center[0],
            distance=round(self.distance, 1),
        )

    def get_geojson(self):
        return self.geojson_dict


@dataclass
class GPXFileMetadata:
    title: str
    sport: str
    date: str
    duration: float
    center_lon: float
    center_lat: float
    distance: float
    zoom_level: int = 12


def convert_timedelta_to_hours(td):
    return int(td.total_seconds() / 60)


def calc_distance_of_points(list_of_tuples: list):
    total_distance = 0
    first_point = None
    for point in list_of_tuples:
        if first_point is None:
            first_point = point
        else:
            dist = distance.geodesic(first_point, point)
            first_point = point
            total_distance += dist.km
    return total_distance * 0.77
