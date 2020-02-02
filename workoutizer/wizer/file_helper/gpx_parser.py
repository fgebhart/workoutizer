import logging

import gpxpy
import gpxpy.gpx

from wizer.gis.gis import calc_distance_of_points
from .lib.parser import Parser

log = logging.getLogger(__name__)


class GPXParser(Parser):
    def __init__(self, path_to_file):
        super(GPXParser, self).__init__(path_to_file)
        self.gpx = None

    def _parse_metadata(self):
        gpx_file = open(self.path, 'r')
        self.name = self.path.split(".gpx")[0].split("/")[-1]
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
        end = all_points_time[-1]
        self.duration = end - start
        log.debug(f"found duration: {self.duration}")
        if self.gpx.time:
            self.date = self.gpx.time
        else:
            self.date = start

    def _parse_coordinates(self):
        for track in self.gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.altitude.append(point.elevation)
                    self.coordinates.append([point.longitude, point.latitude])
        log.debug(f"found number of coordinates: {len(self.coordinates)}")
        log.debug(f"found number of altitudes: {len(self.altitude)}")
        self.distance = round(calc_distance_of_points(self.coordinates), 2)
        log.debug(f"found distance: {self.distance}")
