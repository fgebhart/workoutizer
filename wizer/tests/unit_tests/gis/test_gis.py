import pytest

from wizer.gis.gis import add_elevation_data_to_coordinates, get_total_distance_of_trace


def test_get_total_distance_of_trace__basic():
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0],latitude_list=[0])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0],latitude_list=[0, 1])
    with pytest.raises(ValueError):
        get_total_distance_of_trace(longitude_list=[0, 1],latitude_list=[0])
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[8, 9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[48, 48], latitude_list=[-8, -9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[-8, -9]) == 110.6
    assert get_total_distance_of_trace(longitude_list=[-48, -48], latitude_list=[8, 9]) == 110.6


def test_get_total_distance_of_trace__reversed_points():
    assert get_total_distance_of_trace(longitude_list=[99, 98], latitude_list=[16, 16]) == 107.03


def test_add_elevation_data_to_coordinates():
    assert add_elevation_data_to_coordinates(
        coordinates=[(8, 49), (9, 50), (10, 51)],
        altitude=[248, 249, 250],
    ) == [(8, 49, 248), (9, 50, 249), (10, 51, 250)]
