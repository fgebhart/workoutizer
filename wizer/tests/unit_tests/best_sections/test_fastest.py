import math

from sportgems import find_fastest_section, DistanceTooSmallException
import numpy as np
import pytest

from wizer.best_sections.fastest import _prepare_coordinates_and_times_for_fastest_secions, get_fastest_section
from wizer.configuration import fastest_sections


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
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    result = find_fastest_section(1000, times, coordinates)

    assert result.start == 629
    assert result.end == 719
    assert math.isclose(result.velocity, 2.914, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__gpx(gpx_parser):
    parser = gpx_parser()
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    result = find_fastest_section(1000, times, coordinates)

    assert result.start == 58
    assert result.end == 118
    assert math.isclose(result.velocity, 3.098, abs_tol=0.01)


def test__prepare_coordinates_and_times_for_fastest_secions(fit_parser):
    parser = fit_parser()

    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    # check that lat and lon got zipped together
    for coo, lat, lon in zip(coordinates, parser.latitude_list, parser.longitude_list):
        if np.isnan(coo[0]) or np.isnan(coo[1]):
            assert coo[0] is lat
            assert coo[1] is lon
        else:
            assert coo[0] == lat
            assert coo[1] == lon

    # times should not be modified
    assert parser.timestamps_list == times


def test_get_fastest_section__fit(fit_parser):
    parser = fit_parser()
    assert parser.distance == 5.84

    # test fastest 1km
    res = get_fastest_section(1000, parser)
    assert res.start == 629
    assert res.end == 719
    assert round(res.velocity, 2) == 2.91

    # test fastest 2km
    res = get_fastest_section(2000, parser)
    assert res.start == 537
    assert res.end == 814
    assert round(res.velocity, 2) == 2.33

    # test fastest 5km
    res = get_fastest_section(5000, parser)
    assert res.start == 76
    assert res.end == 1166
    assert round(res.velocity, 2) == 1.84

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
    assert round(res.velocity, 2) == 3.1

    # test fastest 2km
    res = get_fastest_section(2000, parser)
    assert res.start == 54
    assert res.end == 169
    assert round(res.velocity, 2) == 3.06

    # test fastest 5km
    with pytest.raises(
        DistanceTooSmallException, match="Distance of provided input data is too small for requested desired distance."
    ):
        get_fastest_section(5000, parser)


@pytest.mark.parametrize("test_file", ["2020-10-25-10-54-06.fit", "2020-10-25-10-54-06.fit"])
def test_sportgems_fastest_interface__fit_file_which_cause_panic(fit_parser, test_file):
    parser = fit_parser(test_file)
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    for section in fastest_sections:
        result = find_fastest_section(int(1000 * section), times, coordinates)

        # sanity check that no section causes rust panic
        assert result.end != 0
