import logging
from math import cos, sin, atan2, sqrt, radians, degrees
from dataclasses import dataclass

from geopy import distance

log = logging.getLogger(__name__)


@dataclass
class GeoTrace:
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
            dist = distance.geodesic(first_point, point)
            first_point = point
            total_distance += dist.km
    return total_distance * 0.77


def add_elevation_data_to_coordinates(coordinates: list, elevation: list):
    if len(elevation) > len(coordinates):
        log.debug(f"found more elevation points than, cut beginning of elevation list")
        elevation = elevation[len(coordinates)-1:]
    while len(coordinates) > len(elevation):
        log.debug(f"found more coordinates than elevation points, add elevation to end of coordinates list")
        elevation.insert(0, None)
    coordinates_with_elevation = []
    for coordinate, altitude in zip(coordinates, elevation):
        if altitude:
            coordinate.append(altitude)
        coordinates_with_elevation.append(coordinate)
    return coordinates_with_elevation


