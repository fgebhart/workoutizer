import math

from sportgems import find_fastest_section, DistanceTooSmallException
import pytest

from wizer.best_sections.fastest import get_fastest_section
from wizer import configuration


def test_sportgems_fastest_interface__dummy_data():
    # test sportgems interface with the example data given in the repo readme
    coordinates = [(48.123, 9.35), (48.123, 9.36), (48.123, 9.37), (48.123, 9.38)]
    times = [1608228953.8, 1608228954.8, 1608228955.8, 1608228956.8]

    result = find_fastest_section(1000, times, coordinates, tolerance=1000)

    assert result.start == 0
    assert result.end == 1
    assert math.isclose(result.velocity, 743.0908195788583, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__fit(fit_parser):
    parser = fit_parser()
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    result = find_fastest_section(1000, parser.timestamps_list, coordinates)

    assert result.start == 629
    assert result.end == 719
    assert math.isclose(result.velocity, 2.914, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__gpx(gpx_parser):
    parser = gpx_parser()
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    result = find_fastest_section(1000, parser.timestamps_list, coordinates)

    assert result.start == 58
    assert result.end == 118
    assert math.isclose(result.velocity, 3.098, abs_tol=0.01)


def test_get_fastest_section__fit(fit_parser):
    parser = fit_parser()
    assert parser.distance == 5.84

    # test fastest 1km
    res = get_fastest_section(1000, parser)
    assert res.start == 629
    assert res.end == 719
    assert round(res.max_value, 2) == 2.91

    # test fastest 2km
    res = get_fastest_section(2000, parser)
    assert res.start == 537
    assert res.end == 814
    assert round(res.max_value, 2) == 2.33

    # test fastest 5km
    res = get_fastest_section(5000, parser)
    assert res.start == 76
    assert res.end == 1166
    assert round(res.max_value, 2) == 1.84

    # test fastest 10km, in this case the activity data is shorter
    # than 10km and thus we expect that no suitable section was found
    with pytest.raises(
        DistanceTooSmallException, match="Distance of provided input data is too small for requested desired distance."
    ):
        get_fastest_section(10_000, parser)


def test_get_fastest_section__gpx(gpx_parser):
    parser = gpx_parser()
    assert parser.distance == 4.3

    # test fastest 1km
    res = get_fastest_section(1000, parser)
    assert res.start == 58
    assert res.end == 118
    assert round(res.max_value, 2) == 3.1

    # test fastest 2km
    res = get_fastest_section(2000, parser)
    assert res.start == 54
    assert res.end == 169
    assert round(res.max_value, 2) == 3.06

    # test fastest 5km
    with pytest.raises(
        DistanceTooSmallException, match="Distance of provided input data is too small for requested desired distance."
    ):
        get_fastest_section(5000, parser)


@pytest.mark.parametrize("test_file", ["2020-10-25-10-54-06.fit", "2020-10-25-10-54-06.fit"])
def test_sportgems_fastest_interface__fit_file_which_cause_panic(fit_parser, test_file):
    parser = fit_parser(test_file)
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))
    for distance in configuration.fastest_distances:
        result = find_fastest_section(distance, parser.timestamps_list, coordinates)

        # sanity check that no section causes rust panic
        assert result.end != 0


def test_sportgems_fastest_interface__fit_file_without_coordinate_data(fit_parser):
    parser = fit_parser("swim_no_coordinates.fit")
    # set altitude list to empty list to simulate a fit file without altitude data
    for distance in configuration.fastest_distances:
        result = get_fastest_section(distance, parser)

        # sanity check that no section causes rust panic
        assert result is None
