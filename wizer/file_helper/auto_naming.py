from typing import Union
import datetime
import json

import pandas as pd

from wizer.gis.geo import get_location_name


def _get_daytime_name(date: datetime.datetime) -> str:
    hour = date.hour
    if (hour > 4) and (hour <= 8):
        return "Early Morning"
    elif (hour > 8) and (hour <= 12):
        return "Morning"
    elif (hour > 12) and (hour <= 16):
        return "Noon"
    elif (hour > 16) and (hour <= 20):
        return "Evening"
    elif (hour > 20) and (hour <= 24):
        return "Night"
    elif hour <= 4:
        return "Late Night"


def _get_sport_name(sport_name: str) -> str:
    if sport_name == "unknown":
        return "Sport"
    else:
        return sport_name.capitalize()


def _get_coordinate_not_null(coordinates: Union[str, list]):
    try:
        if isinstance(coordinates, str):
            coordinate = pd.Series(json.loads(coordinates), dtype=float).dropna().iloc[0]
        elif isinstance(coordinates, list):
            coordinate = pd.Series(coordinates, dtype=float).dropna().iloc[0]
        else:
            raise NotImplementedError(f"Input coordinates must be either of type list or str - not {type(coordinates)}.")
    except IndexError:
        coordinate = None
    return coordinate


def get_automatic_name(parser, sport_name: str) -> str:
    lat = _get_coordinate_not_null(coordinates=parser.latitude_list)
    lon = _get_coordinate_not_null(coordinates=parser.longitude_list)
    if lat and lon:
        location = get_location_name((lat, lon))
    else:
        location = None
    daytime = _get_daytime_name(parser.date)
    sport = _get_sport_name(sport_name)
    if location:
        return f"{daytime} {sport} in {location}"
    else:
        return f"{daytime} {sport}"
