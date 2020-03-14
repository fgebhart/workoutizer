import os
import datetime


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
        # trace file infos
        # coordinates
        self.coordinates_list = []
        # elevation
        self.altitude_list = []
        # heart rate
        self.heart_rate_list = []
        self.avg_heart_rate = None   # int()
        # cadence
        self.cadence_list = []
        self.avg_cadence = None     # int()
        # speed
        self.speed_list = []
        self.avg_speed = None       # float()
        # temperature
        self.temperature_list = []
        self.avg_temperature = None     # int()
        # training effect
        self.aerobic_training_effect = None     # float()
        self.anaerobic_training_effect = None   # float()

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
