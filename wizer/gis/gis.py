import logging
from dataclasses import dataclass
from typing import List

from geopy import distance

from wizer.tools.utils import cut_list_to_have_same_length

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


def calc_distance_of_points(list_of_coordinates: List[tuple]):
    total_distance = 0
    first_point = None
    for point in list_of_coordinates:
        if first_point is None:
            first_point = point
        else:
            dist = distance.geodesic([p for p in reversed(first_point)], [p for p in reversed(point)])
            first_point = point
            total_distance += dist.km
    return round(total_distance, 2)


def turn_coordinates_into_list_of_distances(list_of_coordinates: List[tuple]):
    """
    Function to calculate the distance between coordinates in a list. Using the
    'great_circle' for measuring here, since it is much faster (but less precise
    than 'geodesic').

    Parameters
    ----------
    list_of_coordinates : List[tuple]
        A list containing tuples with coordinates

    Returns
    -------
    list_of_distances : List[float]
        A list containing the distance in kilometers between two coordinates.
        Subsequent values are added up, thus the values are increasing.
    """

    list_of_distances = []
    previous_coordinates = None
    for coordinates in list_of_coordinates:
        if not previous_coordinates:
            list_of_distances.append(0.)
        else:
            dist = distance.great_circle([previous_coordinates[1], previous_coordinates[0]], [coordinates[1], coordinates[0]])
            list_of_distances.append(round(list_of_distances[-1] + dist.km, 4))
        previous_coordinates = coordinates
    return list_of_distances


def add_elevation_data_to_coordinates(coordinates: list, elevation: list):
    coordinates, elevation = cut_list_to_have_same_length(coordinates, elevation, mode="fill end")
    coordinates_with_elevation = []
    for coordinate, altitude in zip(coordinates, elevation):
        coordinate.append(altitude)
        coordinates_with_elevation.append(coordinate)
    return coordinates_with_elevation
