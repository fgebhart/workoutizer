import logging

import gpxpy
import gpxpy.gpx

from wizer.gis.gis import calc_distance_of_points
from wizer.tools.utils import convert_timedelta_to_hours
from .lib.generic import Parser

log = logging.getLogger('wizer.gpx')


class GPXParser(Parser):
    def __init__(self, path_to_file):
        super(GPXParser, self).__init__(path_to_file)
        self.gpx = None

    def parse_metadata(self):
        gpx_file = open(self.path, 'r')
        self.title = self.path.split(".gpx")[0].split("/")[-1]
        self.gpx = gpxpy.parse(gpx_file)
        self.get_sport_from_gpx_file()
        self.get_duration_from_gpx_file()

    def get_sport_from_gpx_file(self):
        for e in self.gpx.tracks[0].extensions:
            if e.tag.split("}")[1] == "activity":
                self.sport = e.text
                log.debug(f"found sport: {self.sport}")

    def get_duration_from_gpx_file(self):
        all_points_time = []
        for s in self.gpx.tracks[0].segments:
            for p in s.points:
                all_points_time.append(p.time)
        start = all_points_time[0]
        self.date = start
        end = all_points_time[-1]
        self.duration = convert_timedelta_to_hours(end - start)
        log.debug(f"found duration: {self.duration}")

    def parse_coordinates(self):
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.coordinates.append([point.longitude, point.latitude])
        log.debug(f"coordinates: {self.coordinates}")
        self.distance = round(calc_distance_of_points(self.coordinates), 2)
        log.debug(f"found distance: {self.distance}")
