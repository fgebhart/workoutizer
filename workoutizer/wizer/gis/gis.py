import logging
from dataclasses import dataclass

log = logging.getLogger('wizer.gis')


@dataclass
class GeoTrace:
    center_lon: float
    center_lat: float
    coordinates: list
    sport: str
    color: str = '#808080'
    opacity: float = 0.7
    weight: float = 3.0


# geojson = {
#     "type": "FeatureCollection",
#     "name": "tracks",
#     "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
#     "features": [
#         {"type": "Feature",
#          "properties": {"name": name,
#                         "gpx_style_line": "<gpx_style:color>#C71585</gpx_style:color>"
#                                           f"<gpx_style:opacity>{opacity}</gpx_style:opacity>"
#                                           f"<gpx_style:width>{width}</gpx_style:width>",
#                         "locus_activity": sport},
#          "geometry": gemoetry}]}
