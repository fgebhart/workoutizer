import logging
from dataclasses import dataclass
from math import cos, sin, atan2, sqrt, radians, degrees

from geopy import distance
import gpxpy
import gpxpy.gpx
from geojson import MultiLineString, LineString

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


class GPXConverter:
    def __init__(self, path_to_gpx):
        self.path = path_to_gpx
        self.sport = None
        self.duration = None
        self.distance = None
        self.date = None
        self.gpx = None
        self.geojson_multilinestring = None
        self.center = None
        self.coordinates = []

        # run converter
        try:
            self.read_gpx_file()
            self.parse_points()
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
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.coordinates.append([point.longitude, point.latitude])
        self.center = center_geolocation(self.coordinates)
        log.debug(f"center points: {self.center}")
        log.debug(f"coordinates: {self.coordinates}")
        self.distance = calc_distance_of_points(self.coordinates)
        log.debug(f"found distance: {self.distance}")

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

    def get_coordinates(self):
        return self.coordinates


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
