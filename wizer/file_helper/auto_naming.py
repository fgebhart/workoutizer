from typing import Tuple
import datetime

from geopy.geocoders import Nominatim


def _get_location_name(coordinate: Tuple[float, float]) -> str:
    app = Nominatim(user_agent="tutorial")
    try:
        address = app.reverse(coordinate, language="en").raw["address"]
        if "city" in address.keys():
            return address["city"]
        elif "village" in address.keys():
            return address["village"]
    except (TypeError, ValueError):
        return None


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


def get_automatic_name(parser, sport_name: str) -> str:
    location = None
    if parser.latitude_list:
        coordinate = (parser.latitude_list[0], parser.longitude_list[1])
        location = _get_location_name(coordinate)
    daytime = _get_daytime_name(parser.date)
    sport = _get_sport_name(sport_name)
    if location:
        return f"{daytime} {sport} in {location}"
    else:
        return f"{daytime} {sport}"
