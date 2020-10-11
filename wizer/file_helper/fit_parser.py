from dataclasses import dataclass
import json
import logging
import datetime

import pytz
import pandas as pd
from fitparse import FitFile
from django.conf import settings

from wizer.file_helper.lib.parser import Parser
from wizer import naming

log = logging.getLogger(__name__)


class FITParser(Parser):
    def __init__(self, path_to_file):
        self.fit = None
        super(FITParser, self).__init__(path_to_file)

    def _parse_metadata(self):
        self.file_name = self.get_file_name_from_path(self.path_to_file)
        self.fit = FitFile(self.path_to_file)

    def _parse_records(self):
        for record in self.fit.get_messages():
            record = record.get_values()
            # parse laps
            if record.get('event') == 'lap':
                self.laps.append(_parse_lap_data(record))
            
            # parse list attributes
            timestamp = record.get('timestamp')
            self.timestamps_list.append(timestamp.timestamp() if timestamp else timestamp)
            self.distance_list.append(record.get('distance'))
            self.longitude_list.append(_to_coordinate(record.get('position_long')))
            self.latitude_list.append(_to_coordinate(record.get('position_lat')))
            altitude = record.get('altitude')
            self.altitude_list.append((float(altitude) / 10) if altitude else altitude)
            self.heart_rate_list.append(record.get('heart_rate'))
            self.temperature_list.append(record.get('temperature'))
            self.cadence_list.append(record.get('cadence'))
            self.speed_list.append(record.get('enhanced_speed'))

            # get first value of records
            if not self.sport:
                self.sport = record.get("sport")
            if not self.aerobic_training_effect:
                self.aerobic_training_effect = record.get("total_training_effect")
            if not self.anaerobic_training_effect:
                self.anaerobic_training_effect = record.get("total_anaerobic_training_effect")
            
            # get last value of records
            distance = record.get("total_distance")
            if distance:
                self.distance = round(float(distance) / 1000, 2)
            duration = record.get("total_elapsed_time")
            if duration:
                self.duration = datetime.timedelta(seconds=int(duration))
            date = record.get("timestamp")
            if date:
                self.date = date.replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
            calories = record.get("total_calories")
            if calories:
                self.calories = calories
            avg_heart_rate = record.get("avg_heart_rate")
            if avg_heart_rate:
                self.avg_heart_rate = avg_heart_rate
            avg_cadence = record.get("avg_running_cadence")
            if avg_cadence:
                self.avg_cadence = avg_cadence
            avg_speed = record.get("enhanced_avg_speed")
            if avg_speed:
                self.avg_speed = avg_speed
            avg_temperature = record.get("avg_temperature")
            if avg_temperature:
                self.avg_temperature = avg_temperature
            
        log.debug(f"found date: {self.date}")
        log.debug(f"found number of coordinates: {len(self.longitude_list)}")
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
            if attribute in naming.min_max_attributes:
                name = attribute.replace("_list", "")
                values = pd.Series(values)
                if values.any():
                    setattr(self, f"max_{name}", round(float(values.max()), 2))
                    setattr(self, f"min_{name}", round(float(values.min()), 2))

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
