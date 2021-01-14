import os
import datetime

from wizer.best_sections.fastest import get_fastest_section, FastestSection
from wizer.configuration import fastest_sections


class Parser:
    def __init__(self, path_to_file):
        # basic activity info
        self.path_to_file = path_to_file
        self.file_name = None
        self.sport = None
        self.date = None
        self.duration = datetime.timedelta(minutes=0)
        self.distance = 0
        self.calories = None
        # trace file info
        # coordinates
        self.latitude_list = []
        self.longitude_list = []
        # distances
        self.distance_list = []
        # elevation
        self.altitude_list = []
        self.min_altitude = None  # float()
        self.max_altitude = None
        # heart rate
        self.heart_rate_list = []
        self.min_heart_rate = None
        self.avg_heart_rate = None  # int()
        self.max_heart_rate = None
        # cadence
        self.cadence_list = []
        self.min_cadence = None
        self.avg_cadence = None  # int()
        self.max_cadence = None
        # speed
        self.speed_list = []
        self.min_speed = None
        self.avg_speed = None  # float()
        self.max_speed = None
        # temperature
        self.temperature_list = []
        self.min_temperature = None
        self.avg_temperature = None  # int()
        self.max_temperature = None
        # training effect
        self.aerobic_training_effect = None  # float()
        self.anaerobic_training_effect = None  # float()
        # timestamps
        self.timestamps_list = []
        # lists
        self.list_attributes = [
            self.timestamps_list,
            self.longitude_list,
            self.latitude_list,
            self.temperature_list,
            self.cadence_list,
            self.altitude_list,
            self.speed_list,
            self.heart_rate_list,
        ]
        # lap info
        self.laps = []

        # fastest sections
        self.best_sections = []

        # run parser
        self._parse_metadata()
        self._parse_records()

    def _parse_metadata(self):
        raise NotImplementedError

    def _parse_records(self):
        raise NotImplementedError

    def get_file_created_datetime(self):
        self.date = datetime.datetime.fromtimestamp(os.path.getctime(self.path_to_file)).date()

    def get_file_name_from_path(self, path):
        return path.split("/")[-1]

    def get_fastest_sections(self):
        for section_distance in fastest_sections:
            if self.distance > section_distance:
                found_section, start_index, end_index, velocity = get_fastest_section(int(section_distance * 1000), self)
                if found_section:
                    sec = FastestSection(
                        start_index=start_index,
                        end_index=end_index,
                        section_distance=section_distance,
                        max_value=velocity,
                    )
                    self.best_sections.append(sec)
