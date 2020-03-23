from wizer.file_helper.gpx_parser import calc_distance_of_points
from wizer.gis.gis import add_elevation_data_to_coordinates


def test_calc_distance_of_points():
    assert calc_distance_of_points([(48, 8), (48, 9)]) == 110.6
    assert calc_distance_of_points([(48, -8), (48, -9)]) == 110.6
    assert calc_distance_of_points([(-48, -8), (-48, -9)]) == 110.6
    assert calc_distance_of_points([(-48, 8), (-48, 9)]) == 110.6


def test_calc_distance_of_points_reversed_points():
    assert calc_distance_of_points([(99, 16), (98, 16)]) == 107.03


def test_add_elevation_data_to_coordinates():
    assert add_elevation_data_to_coordinates(
        coordinates=[[8, 49], [9, 50], [10, 51]],
        elevation=[248, 249, 250],
    ) == [[8, 49, 248], [9, 50, 249], [10, 51, 250]]

