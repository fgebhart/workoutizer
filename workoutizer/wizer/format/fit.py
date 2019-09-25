import logging
import datetime

from fitparse import FitFile
from wizer.format.lib.generic import Parser

log = logging.getLogger('wizer.fit')


# coordinates conversion parameter
ccp = 11930464.71111111


class FITParser(Parser):
    def __init__(self, path_to_file):
        super(FITParser, self).__init__(path_to_file)
        self.fit = None

    def parse_metadata(self):
        self.name = self.path.split(".fit")[0].split("/")[-1]
        self.fit = FitFile(self.path)
        self.get_sport_duration_distance()
        # log.debug(f"fit file: {self.fit.messages}")

    def get_sport_duration_distance(self):
        sport = None
        distance = None
        duration = None
        date = None
        for record in self.fit.get_messages():
            for k, v in record.get_values().items():
                if k == 'sport':
                    sport = v
                elif k == "total_distance":
                    distance = v
                elif k == "total_elapsed_time":
                    duration = v
                elif k == "timestamp":
                    date = v
        self.distance = round(float(distance)/1000, 2)
        self.sport = sport
        self.duration = datetime.timedelta(seconds=duration)
        self.date = date
        log.debug(f"found sport: {self.sport}")
        log.debug(f"found distance: {self.distance} km")
        log.debug(f"found duration: {self.duration} min")
        log.debug(f"found date: {self.date}")

    def parse_coordinates(self):
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
                    self.altitude.append(float(record_data.value)/10)
            if lat and lon:
                coordinates.append([float(lon)/ccp, float(lat)/ccp])
        self.coordinates = coordinates
        # NOTE: There might be more altitude values than coordinates, since garmin start activity even if there is
        # NOTE: no GPS signal yet...
        log.debug(f"found number of coordinates: {len(self.coordinates)}")
        log.debug(f"found number of altitudes: {len(self.altitude)}")
