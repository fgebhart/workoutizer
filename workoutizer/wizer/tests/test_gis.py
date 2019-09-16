from wizer.gis.gpx_converter import calc_distance_of_points
from wizer.gis.gis import bounding_coordinates


def test_calc_distance_of_points():
    assert int(calc_distance_of_points([(41.49008, -71.312796), (41.499498, -81.695391)])) == int(667)


def test_bounding_coordinates():
    my_coordinates = [
        [56.270253, 47.913832],
        [54.120152, -66.048803],
        [21.117752, -77.546458],
        [-23.463165, 19.257547],
        [49.401472, 8.699944]
    ]
    assert bounding_coordinates(my_coordinates) == [[56.270253, 47.913832], [-23.463165, -77.546458]]
