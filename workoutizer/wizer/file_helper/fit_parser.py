import logging
import datetime

from fitparse import FitFile
from wizer.file_helper.lib.parser import Parser

log = logging.getLogger(__name__)


# coordinates conversion parameter
ccp = 11930464.71111111


class FITParser(Parser):
    def __init__(self, path_to_file):
        self.fit = None
        super(FITParser, self).__init__(path_to_file)

    def _parse_metadata(self):
        self.name = self.path.split(".fit")[0].split("/")[-1]
        self.fit = FitFile(self.path)
        self._get_sport_duration_distance()

    def _get_sport_duration_distance(self):
        sport = None
        distance = None
        duration = None
        date = None
        for record in self.fit.get_messages():
            for label, value in record.get_values().items():
                if label == 'sport':
                    sport = value
                elif label == "total_distance":
                    distance = value
                elif label == "total_elapsed_time":
                    duration = value
                elif label == "timestamp":
                    date = value
        self.distance = round(float(distance)/1000, 2)
        self.sport = sport
        self.duration = datetime.timedelta(seconds=int(duration))
        self.date = date
        log.debug(f"found sport: {self.sport}")
        log.debug(f"found distance: {self.distance} km")
        log.debug(f"found duration: {self.duration} min")
        log.debug(f"found date: {self.date}")

    def _parse_coordinates(self):
        coordinates = []
        lon = None
        lat = None
        for record in self.fit.get_messages('record'):
            for record_data in record:
                if record_data.name == "position_long":
                    lon = record_data.value
                if record_data.name == "position_lat":
                    lat = record_data.value
                if record_data.name == "altitude":
                    self.elevation.append(float(record_data.value)/10)
            if lat and lon:
                coordinates.append([float(lon)/ccp, float(lat)/ccp])
        self.coordinates = coordinates
        # NOTE: There might be more altitude values than coordinates, since garmin start activity even if there is
        # NOTE: no GPS signal yet...
        log.debug(f"found number of coordinates: {len(self.coordinates)}")
        log.debug(f"found number of elevation: {len(self.elevation)}")

    def parse_heart_rate(self):
        heart_rate = []
        for record in self.fit.get_messages('record'):
            for record_data in record:
                if record_data.name == "heart_rate":
                    heart_rate.append(record_data.value)
        self.heart_rate = heart_rate

    def parse_calories(self):
        for record in self.fit.get_messages():
            for label, value in record.get_values().items():
                if label == 'total_calories':
                    self.calories = value
