import math

from sportgems import find_best_climb_section, DistanceTooSmallException
import pytest

from wizer.best_sections.climb import get_best_climb_section
from wizer import configuration


def test_sportgems_climb_interface__dummy_data():
    # test sportgems interface with the example data given in the repo readme
    coordinates = [(48.123, 9.35), (48.123, 9.36), (48.123, 9.37), (48.123, 9.38)]
    altitudes = [123.4, 234.5, 345.6, 456.7]
    times = [1608228953.8, 1608228954.8, 1608228955.8, 1608228956.8]

    result = find_best_climb_section(1000, times, coordinates, altitudes, tolerance=1000)

    assert result.start == 0
    assert result.end == 3
    assert math.isclose(result.climb, 4444.0, abs_tol=0.01)


def test_sportgems_climb_interface__real_activity_data__fit(fit_parser):
    parser = fit_parser()
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    result = find_best_climb_section(1000, parser.timestamps_list, coordinates, parser.altitude_list)

    assert result.start == 339
    assert result.end == 580
    assert math.isclose(result.climb, 5.786, abs_tol=0.01)


def test_sportgems_climb_interface__real_activity_data__gpx(gpx_parser):
    parser = gpx_parser()
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    result = find_best_climb_section(1000, parser.timestamps_list, coordinates, parser.altitude_list)

    assert result.start == 175
    assert result.end == 239
    assert math.isclose(result.climb, 10.617, abs_tol=0.01)


def test_get_best_climb_section__fit(fit_parser):
    parser = fit_parser()
    assert parser.distance == 5.84

    # test fastest 1km
    res = get_best_climb_section(1000, parser)
    assert res.start == 339
    assert res.end == 580
    assert round(res.max_value, 2) == 5.78

    # test fastest 2km
    res = get_best_climb_section(2000, parser)
    assert res.start == 50
    assert res.end == 584
    assert round(res.max_value, 2) == 5.0

    # test fastest 5km
    res = get_best_climb_section(5000, parser)
    assert res.start == 52
    assert res.end == 1151
    assert round(res.max_value, 2) == 2.36

    # test fastest 10km, in this case the activity data is shorter
    # than 10km and thus we expect that no suitable section was found
    with pytest.raises(
        DistanceTooSmallException, match="Distance of provided input data is too small for requested desired distance."
    ):
        get_best_climb_section(10_000, parser)


def test_get_best_climb_section__gpx(gpx_parser):
    parser = gpx_parser()
    assert parser.distance == 4.3

    # test fastest 1km
    res = get_best_climb_section(1000, parser)
    assert res.start == 175
    assert res.end == 239
    assert round(res.max_value, 2) == 10.62

    # test fastest 2km
    res = get_best_climb_section(2000, parser)
    assert res.start == 111
    assert res.end == 240
    assert round(res.max_value, 2) == 9.64

    # test fastest 5km
    with pytest.raises(
        DistanceTooSmallException, match="Distance of provided input data is too small for requested desired distance."
    ):
        get_best_climb_section(5000, parser)


def test_sportgems_climb_interface__fit_file_without_altitude_data(fit_parser):
    parser = fit_parser("2020-09-12-11-15-46.fit")
    # set altitude list to empty list to simulate a fit file without altitude data
    parser.altitude_list = []
    for distance in configuration.climb_distances:
        result = get_best_climb_section(distance, parser)

        # sanity check that no section causes rust panic
        assert result is None
