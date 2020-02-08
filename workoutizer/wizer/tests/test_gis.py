from wizer.file_helper.gpx_parser import calc_distance_of_points
from wizer.gis.gis import add_elevation_data_to_coordinates


def test_calc_distance_of_points():
    assert int(calc_distance_of_points([(41.49008, -71.312796), (41.499498, -81.695391)])) == int(667)


def test_add_elevation_data_to_coordinates():
    # in case both lists have same length
    assert add_elevation_data_to_coordinates(
        coordinates=[[8.7, 49.5], [8.7, 49.6], [8.7, 49.6]],
        elevation=[248.7, 248.6, 248.5],
    ) == [[8.7, 49.5, 248.7], [8.7, 49.6, 248.6], [8.7, 49.6, 248.5]]
    # in case there are more elevation points (more likely the case) -> cut beginning of elevation
    assert add_elevation_data_to_coordinates(
        coordinates=[[8.7, 49.5], [8.7, 49.6], [8.7, 49.6]],
        elevation=[248.9, 248.8, 248.7, 248.6, 248.5],
    ) == [[8.7, 49.5, 248.7], [8.7, 49.6, 248.6], [8.7, 49.6, 248.5]]
    # in case there are more coordinates (less likely the case) -> skip first coordinates
    assert add_elevation_data_to_coordinates(
        coordinates=[[8.7, 49.5], [8.7, 49.6], [8.7, 49.7], [8.7, 49.8], [8.7, 49.9]],
        elevation=[248.7, 248.6, 248.5],
    ) == [[8.7, 49.5], [8.7, 49.6], [8.7, 49.7, 248.7], [8.7, 49.8, 248.6], [8.7, 49.9, 248.5]]
