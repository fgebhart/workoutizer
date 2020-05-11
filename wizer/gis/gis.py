import logging
from math import cos, sin, atan2, sqrt, radians, degrees
from dataclasses import dataclass
from wizer.tools.utils import ensure_lists_have_same_length

from geopy import distance

log = logging.getLogger(__name__)


@dataclass
class GeoTrace:
    pk: int
    name: str
    coordinates: list
    sport: str
    color: str = '#808080'
    opacity: float = 0.7
    weight: float = 3.0


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


def calc_distance_of_points(list_of_tuples: list):
    total_distance = 0
    first_point = None
    for point in list_of_tuples:
        if first_point is None:
            first_point = point
        else:
            dist = distance.geodesic([p for p in reversed(first_point)], [p for p in reversed(point)])
            first_point = point
            total_distance += dist.km
    return round(total_distance, 2)


def add_elevation_data_to_coordinates(coordinates: list, elevation: list):
    coordinates, elevation = ensure_lists_have_same_length(coordinates, elevation, mode="fill end")
    coordinates_with_elevation = []
    for coordinate, altitude in zip(coordinates, elevation):
        coordinate.append(altitude)
        coordinates_with_elevation.append(coordinate)
    return coordinates_with_elevation


