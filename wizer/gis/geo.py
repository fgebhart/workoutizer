import logging
import json
from dataclasses import dataclass
from typing import List, Tuple


from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd

log = logging.getLogger(__name__)


@dataclass
class GeoTrace:
    pk: int
    name: str
    coordinates: list
    sport: str
    color: str = "#808080"
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
            point = (row["lat"], row["lon"])
            next_point = (coordinates_df.at[index + 1, "lat"], coordinates_df.at[index + 1, "lon"])
            dist = distance.geodesic(point, next_point)
            total_distance += dist.km
    return round(total_distance, 2)


def add_elevation_data_to_coordinates(coordinates: list, altitude: list):
    coordinates_with_elevation = []
    for coordinate, altitude in zip(coordinates, altitude):
        coordinate = coordinate + (altitude,)
        coordinates_with_elevation.append(coordinate)
    return coordinates_with_elevation


def get_location_name(coordinate: Tuple[float, float]) -> str:
    app = Nominatim(user_agent="tutorial")
    try:
        address = app.reverse(coordinate, language="en", timeout=5).raw["address"]
        # use name of location from village, town or city (in this order)
        if "village" in address.keys():
            return address["village"]
        elif "town" in address.keys():
            return address["town"]
        elif "city" in address.keys():
            return address["city"]
    except (TypeError, ValueError):
        return None


def get_list_of_coordinates(list_of_lon: List[float], list_of_lat: List[float]) -> List[Tuple[float]]:
    return json.dumps(
        list(
            zip(
                list(pd.Series(json.loads(list_of_lon)).ffill().bfill()),
                list(pd.Series(json.loads(list_of_lat)).ffill().bfill()),
            )
        )
    )
