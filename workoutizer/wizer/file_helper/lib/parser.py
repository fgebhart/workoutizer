import os
import datetime


class Parser:
    def __init__(self, path_to_file):
        self.path = path_to_file
        self.name = None
        self.sport = None
        self.duration = datetime.timedelta(minutes=0)
        self.distance = 0
        self.date = None
        self.coordinates = []
        self.elevation = []
        self.heart_rate = []
        self.calories = int()

        # run parser
        self._parse_metadata()
        self._parse_coordinates()

    def _parse_metadata(self):
        raise NotImplementedError

    def _parse_coordinates(self):
        raise NotImplementedError

    def get_file_created_datetime(self):
        self.date = datetime.datetime.fromtimestamp(os.path.getctime(self.path)).date()
