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
