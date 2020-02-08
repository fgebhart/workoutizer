from wizer.file_helper.gpx_parser import calc_distance_of_points
from wizer.gis.gis import add_elevation_data_to_coordinates


def test_calc_distance_of_points():
    assert int(calc_distance_of_points([(41.49008, -71.312796), (41.499498, -81.695391)])) == int(667)


def test_add_elevation_data_to_coordinates():
    # in case both lists have same length
    assert add_elevation_data_to_coordinates(
        coordinates=[[8, 49], [9, 50], [10, 51]],
        elevation=[248, 249, 250],
    ) == [[8, 49, 248], [9, 50, 249], [10, 51, 250]]
    # in case there are more elevation points (more likely the case) -> cut beginning of elevation
    assert add_elevation_data_to_coordinates(
        coordinates=[[8, 49], [9, 50], [10, 51]],
        elevation=[246, 247, 248, 249, 250, 251, 252],
    ) == [[8, 49, 250], [9, 50, 251], [10, 51, 252]]
    # in case there are more coordinates (less likely the case) -> skip first coordinates
    assert add_elevation_data_to_coordinates(
        coordinates=[[8, 49], [9, 50], [10, 51], [11, 52], [12, 53]],
        elevation=[248, 249, 250],
    ) == [[8, 49], [9, 50], [10, 51, 248], [11, 52, 249], [12, 53, 250]]
