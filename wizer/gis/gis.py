import logging
from dataclasses import dataclass
from typing import List

from geopy import distance
import pandas as pd

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


def get_total_distance_of_trace(longitude_list: List[float], latitude_list: List[float]):
    if len(latitude_list) != len(longitude_list):
        raise ValueError("lat and lon lists need to have same length")
    if len(latitude_list) < 2 or len(longitude_list) < 2:
        raise ValueError("lat and lon lists need to be at least of length 2")
    coordinates_df = pd.DataFrame({"lat": latitude_list, "lon": longitude_list})
    coordinates_df.dropna(inplace=True)

    total_distance = 0
    for index, row in coordinates_df.iterrows():
        if index < len(coordinates_df) - 1:
            point = (row['lat'], row['lon'])
            next_point = (coordinates_df.at[index + 1, 'lat'], coordinates_df.at[index + 1, 'lon'])
            dist = distance.geodesic(point, next_point)
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


def add_elevation_data_to_coordinates(coordinates: list, altitude: list):
    coordinates, altitude = cut_list_to_have_same_length(coordinates, altitude, mode="fill end")
    coordinates_with_elevation = []
    for coordinate, altitude in zip(coordinates, altitude):
        coordinate.append(altitude)
        coordinates_with_elevation.append(coordinate)
    return coordinates_with_elevation
