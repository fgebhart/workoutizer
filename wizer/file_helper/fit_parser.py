from dataclasses import dataclass
import json
import logging
import datetime

import pytz
from fitparse import FitFile
from django.conf import settings

from wizer.file_helper.lib.parser import Parser
from wizer.tools.utils import remove_nones_from_list

log = logging.getLogger(__name__)


class FITParser(Parser):
    def __init__(self, path_to_file):
        self.fit = None
        super(FITParser, self).__init__(path_to_file)

    def _parse_metadata(self):
        self.file_name = self.get_file_name_from_path(self.path_to_file)
        self.fit = FitFile(self.path_to_file)

    def _parse_records(self):
        coordinates = []
        lon = None
        lat = None
        altitude = None
        for record in self.fit.get_messages():
            # print(f"------------------------------ new record ------------------------------")
            record = record.get_values()
            if record.get('event') == 'lap':
                self.laps.append(_parse_lap_data(record))
            for label, value in record.items():
                # print(f"{label}: {value}")
                if label == 'sport':
                    self.sport = value
                if label == "total_distance":
                    self.distance = round(float(value) / 1000, 2)
                if label == "total_elapsed_time":
                    self.duration = datetime.timedelta(seconds=int(value))
                if label == "timestamp":
                    self.date = value.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
                # calories
                if label == 'total_calories':
                    self.calories = value
                # speed
                if label == "enhanced_speed":
                    self.speed_list.append(value if value else 0)
                if label == "enhanced_avg_speed":
                    self.avg_speed = value
                # coordinates
                if label == "position_long":
                    lon = value
                if label == "position_lat":
                    lat = value
                # distances
                if label == "distance":
                    self.distance_list.append(value)
                # altitude
                if label == "altitude":
                    altitude = float(value) / 10
                # heart rate
                if label == "heart_rate":
                    self.heart_rate_list.append(value)
                if label == "avg_heart_rate":
                    self.avg_heart_rate = value
                # cadence
                if label == 'cadence':
                    self.cadence_list.append(value if value else 0)
                if label == "avg_running_cadence":
                    self.avg_cadence = value
                # temperature
                if label == "temperature":
                    self.temperature_list.append(value)
                if label == "avg_temperature":
                    self.avg_temperature = value
                # training effect
                if label == "total_training_effect":
                    self.aerobic_training_effect = value
                if label == "total_anaerobic_training_effect":
                    self.anaerobic_training_effect = value
                # timestamps
                if label == "timestamp":
                    self.timestamps_list.append(value.timestamp())
            if lat and lon:
                coordinates.append([_to_coordinate(lon), _to_coordinate(lat)])
                self.altitude_list.append(altitude)
        self.coordinates_list = coordinates
        log.debug(f"found date: {self.date}")
        log.debug(f"found number of coordinates: {len(self.coordinates_list)}")
        log.debug(f"found number of altitude: {len(self.altitude_list)}")
        log.debug(f"found number of timestamps: {len(self.timestamps_list)}")
        log.debug(f"found avg_speed: {self.avg_speed}")
        log.debug(f"found sport: {self.sport}")
        log.debug(f"found distance: {self.distance} km")
        log.debug(f"found duration: {self.duration} min")
        log.debug(f"found avg_cadence: {self.avg_cadence} steps/min")
        log.debug(f"found avg_temperature: {self.avg_temperature} Celcius")
        log.debug(f"found number of laps: {len(self.laps)}")

    def convert_list_of_nones_to_empty_list(self):
        for attribute, values in self.__dict__.items():
            if attribute.endswith("_list"):
                got_value = False
                for item in getattr(self, attribute):
                    if item:
                        got_value = True
                        break
                if not got_value:
                    setattr(self, attribute, [])

    def set_min_max_values(self):
        attributes = self.__dict__.copy()
        for attribute, values in attributes.items():
            if attribute.endswith("_list") and attribute != 'coordinates_list' and attribute != 'timestamps_list':
                name = attribute.replace("_list", "")
                values = remove_nones_from_list(values)
                if values:
                    setattr(self, f"max_{name}", round(float(max(values)), 2))
                    setattr(self, f"min_{name}", round(float(min(values)), 2))

    def convert_list_attributes_to_json(self):
        for attribute, values in self.__dict__.items():
            if attribute.endswith("_list"):
                setattr(self, attribute, json.dumps(values))


def _parse_lap_data(record):
    lap = LapData(
        start_time=record['start_time'].replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
        end_time=record['timestamp'].replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
        elapsed_time=datetime.timedelta(seconds=record['total_elapsed_time']),
        trigger=record.get('lap_trigger', 'unknown'),
        # lap trigger could be 'manual', 'distance' or 'session_end'
        distance=record['total_distance'],
        start_lat=_to_coordinate(record.get('start_position_lat')),
        start_long=_to_coordinate(record.get('start_position_long')),
        end_lat=_to_coordinate(record.get('end_position_lat')),
        end_long=_to_coordinate(record.get('end_position_long')),
    )

    if lap.elapsed_time and lap.distance:
        lap.speed = round(lap.distance / record['total_elapsed_time'], 2)
    return lap


@dataclass
class LapData:
    start_time: datetime.datetime
    end_time: datetime.datetime
    elapsed_time: datetime.timedelta
    trigger: str
    distance: float = None
    start_lat: float = None
    start_long: float = None
    end_long: float = None
    end_lat: float = None
    speed: float = None


def _to_coordinate(point: int):
    if not point:
        return point
    # coordinates conversion parameter, not sure why this was needed, maybe due to swapping lat with lon?
    ccp = 11930464.71111111

    coordinate = float(point) / ccp
    return coordinate
