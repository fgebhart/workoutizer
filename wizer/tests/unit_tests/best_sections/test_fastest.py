import math

from sportgems import find_fastest_section, DistanceTooSmallException
import pandas as pd
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

    assert result.start == 577
    assert result.end == 666
    assert math.isclose(result.velocity, 2.9142410749856014, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__gpx(gpx_parser):
    parser = gpx_parser()
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    result = find_fastest_section(1000, times, coordinates)

    assert result.start == 58
    assert result.end == 118
    assert math.isclose(result.velocity, 3.098, abs_tol=0.01)


def test__prepare_coordinates_and_times_for_fastest_secions__fit(fit_parser):
    parser = fit_parser()

    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    # check that no null values are present anymore
    assert len(times) == len(coordinates)
    assert pd.Series(times).notna().all()
    # unzip list of tuples to two lists
    lon = []
    lat = []
    for coordinate in coordinates:
        lon.append(coordinate[0])
        lat.append(coordinate[1])
    assert pd.Series(lon).notna().all()
    assert pd.Series(lat).notna().all()

    # check that length was decreased
    assert len(parser.longitude_list) > len(lon)
    assert len(parser.latitude_list) > len(lat)


def test__prepare_coordinates_and_times_for_fastest_secions__gpx(gpx_parser):
    parser = gpx_parser()

    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    # sanity checks that nothing got corrupted
    assert times == parser.timestamps_list
    assert len(times) == len(coordinates)
    assert len(parser.latitude_list) == len(coordinates)
    assert len(parser.longitude_list) == len(coordinates)

    # check that no null values are present anymore
    assert len(times) == len(coordinates)
    assert pd.Series(times).notna().all()
    # unzip list of tuples to two lists
    lon = []
    lat = []
    for coordinate in coordinates:
        lat.append(coordinate[0])
        lon.append(coordinate[1])
    assert pd.Series(lon).notna().all()
    assert pd.Series(lat).notna().all()

    # quantitative checks
    before_df = pd.DataFrame(
        {
            "times": parser.timestamps_list,
            "lon": parser.longitude_list,
            "lat": parser.latitude_list,
        }
    )
    after_df = pd.DataFrame(
        {
            "times": times,
            "lon": lon,
            "lat": lat,
        }
    )

    pd.testing.assert_frame_equal(before_df, after_df)


def test_get_fastest_section__fit(fit_parser):
    parser = fit_parser()
    assert parser.distance == 5.84

    # test fastest 1km
    start, end, velocity = get_fastest_section(1000, parser)
    assert start == 577
    assert end == 666
    assert velocity == 2.91

    # test fastest 2km
    start, end, velocity = get_fastest_section(2000, parser)
    assert start == 485
    assert end == 760
    assert velocity == 2.33

    # test fastest 5km
    start, end, velocity = get_fastest_section(5000, parser)
    assert start == 27
    assert end == 1109
    assert velocity == 1.84

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
    start, end, velocity = get_fastest_section(1000, parser)
    assert start == 58
    assert end == 118
    assert velocity == 3.1

    # test fastest 2km
    start, end, velocity = get_fastest_section(2000, parser)
    assert start == 54
    assert end == 169
    assert velocity == 3.06

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
