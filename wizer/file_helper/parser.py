import os
import datetime
import logging
from typing import List

from wizer import configuration

from sportgems import DistanceTooSmallException, TooFewDataPointsException, NoSectionFoundException


log = logging.getLogger(__name__)


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

        # best sections
        self.best_sections = []

        # run parser
        self._parse_metadata()
        self._parse_records()
        self._post_process_data()

    def _parse_metadata(self):
        raise NotImplementedError

    def _parse_records(self):
        raise NotImplementedError

    def _post_process_data(self):
        raise NotImplementedError

    def get_file_created_datetime(self):
        self.date = datetime.datetime.fromtimestamp(os.path.getctime(self.path_to_file)).date()

    def get_file_name_from_path(self, path):
        return path.split("/")[-1]

    def get_best_sections(self):
        log.debug("parsing best sections using sportgems...")
        # helper func to be called for each available section kind parser

        def _get_best_sections_for_section_kind(section_parser, section_distances: List[int]):
            for distance in section_distances:
                if self.distance * 1000 > distance and self.latitude_list:
                    try:
                        result = section_parser(distance, self)
                        if result:
                            self.best_sections.append(result)
                    except (DistanceTooSmallException, TooFewDataPointsException, NoSectionFoundException) as e:
                        # catching some of the sportgems customs exceptions and logging it
                        log.warning(f"Could not find fastest section. Sportgems error: {e}")
                        # however some are not caught and should actually be raised, e.g. InconsistentLengthException,
                        # NoSectionFoundException and InvalidDesiredDistanceException

        for bs in configuration.best_sections:
            _get_best_sections_for_section_kind(bs["parser"], bs["distances"])
