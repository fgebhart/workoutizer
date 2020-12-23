import pytest

from wizer.gis.geo import add_elevation_data_to_coordinates, get_total_distance_of_trace, get_location_name


def test_get_total_distance_of_trace__basic():
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0], latitude_list=[0])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0], latitude_list=[0, 1])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0, 1], latitude_list=[0])
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[8, 9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[-8, -9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[-8, -9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[8, 9]) == 110.6


def test_get_total_distance_of_trace__reversed_points():
    assert get_total_distance_of_trace(longitude_list=[99, 98], latitude_list=[16, 16]) == 107.03


def test_add_elevation_data_to_coordinates():
    assert (
        add_elevation_data_to_coordinates(
            coordinates=[(8, 49), (9, 50), (10, 51)],
            altitude=[248, 249, 250],
        )
        == [(8, 49, 248), (9, 50, 249), (10, 51, 250)]
    )


def test__get_location_name():
    coordinate = (48.1234, 8.9123)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Heidenstadt"

    coordinate = (49.47950, 8.47102)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Mannheim"

    # this would raise an exception in geopy so we expect to get None
    coordinate = (-90, 90)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name is None

    # also this would raise an exception, however this
    # is not the location which is supposed to fail
    coordinate = (-1000, 90)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name is None


def test_get_other_location_names():
    coordinate = (49.46278064511717, 8.160513974726202)
    location_name = get_location_name(coordinate=coordinate)
    assert location_name == "Bad Dürkheim"
