import json
import logging
import datetime

from fitparse import FitFile
from wizer.file_helper.lib.parser import Parser
from wizer.tools.utils import remove_nones_from_list

log = logging.getLogger(__name__)


# coordinates conversion parameter, not sure why this was needed, maybe due to swapping lat with lon
ccp = 11930464.71111111


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
            for label, value in record.get_values().items():
                # print(f"{label}: {value}")
                if label == 'sport':
                    self.sport = value
                if label == "total_distance":
                    self.distance = round(float(value) / 1000, 2)
                if label == "total_elapsed_time":
                    self.duration = datetime.timedelta(seconds=int(value))
                if label == "timestamp":
                    self.date = value
                # calories
                if label == 'total_calories':
                    self.calories = value
                # speed
                if label == "enhanced_speed":
                    self.speed_list.append(value)
                if label == "enhanced_avg_speed":
                    self.avg_speed = value
                # coordinates
                if label == "position_long":
                    lon = value
                if label == "position_lat":
                    lat = value
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
                    self.cadence_list.append(value)
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
                coordinates.append([float(lon) / ccp, float(lat) / ccp])
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
