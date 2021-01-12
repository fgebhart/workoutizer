import math

from sportgems import find_gems
import pandas as pd
import pytest

from wizer.best_sections.fastest import _prepare_coordinates_and_times_for_fastest_secions, get_fastest_section
from wizer.configuration import fastest_sections


def test_sportgems_fastest_interface__dummy_data():
    # test sportgems interface with the example data given in the repo readme
    fastest_1km = 1000  # in meter
    coordinates = [(48.123, 9.35), (48.123, 9.36), (48.123, 9.37), (48.123, 9.38)]
    times = [1608228953.8, 1608228954.8, 1608228955.8, 1608228956.8]

    result = find_gems(fastest_1km, times, coordinates)

    found_section = result[0]
    start_index = result[1]
    end_index = result[2]
    velocity = result[3]
    assert found_section is True
    assert start_index == 1
    assert end_index == 2
    assert math.isclose(velocity, 743.0908195788583, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__fit(fit_parser):
    parser = fit_parser()
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    result_1km = find_gems(1000, times, coordinates)

    found_section = result_1km[0]
    start_index = result_1km[1]
    end_index = result_1km[2]
    velocity = result_1km[3]
    assert found_section is True
    assert start_index == 577
    assert end_index == 666
    assert math.isclose(velocity, 2.9142410749856014, abs_tol=0.01)


def test_sportgems_fastest_interface__real_activity_data__gpx(gpx_parser):
    parser = gpx_parser()
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    result_1km = find_gems(1000, times, coordinates)

    found_section = result_1km[0]
    start_index = result_1km[1]
    end_index = result_1km[2]
    velocity = result_1km[3]
    assert found_section is True
    assert start_index == 54
    assert end_index == 103
    assert math.isclose(velocity, 3.1352588094779272, abs_tol=0.01)


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

    # test fastest 1km
    found_section, start_index, end_index, velocity = get_fastest_section(1000, parser)
    assert found_section is True
    assert start_index == 577
    assert end_index == 666
    assert velocity == 2.91

    # test fastest 2km
    found_section, start_index, end_index, velocity = get_fastest_section(2000, parser)
    assert found_section is True
    assert start_index == 485
    assert end_index == 760
    assert velocity == 2.33

    # test fastest 5km
    found_section, start_index, end_index, velocity = get_fastest_section(5000, parser)
    assert found_section is True
    assert start_index == 27
    assert end_index == 1109
    assert velocity == 1.84

    # test fastest 10km, in this case the activity data is shorter
    # than 10km and thus we expect that no suitable section was found
    found_section, start_index, end_index, velocity = get_fastest_section(10_000, parser)
    assert found_section is False
    assert start_index == 0
    assert end_index == 0
    assert velocity == 0.0


def test_get_fastest_section__gpx(gpx_parser):
    parser = gpx_parser()
    assert parser.distance == 4.3

    # test fastest 1km
    found_section, start_index, end_index, velocity = get_fastest_section(1000, parser)
    assert found_section is True
    assert start_index == 54
    assert end_index == 103
    assert velocity == 3.14

    # test fastest 2km
    found_section, start_index, end_index, velocity = get_fastest_section(2000, parser)
    assert found_section is True
    assert start_index == 54
    assert end_index == 167
    assert velocity == 3.07

    # test fastest 5km
    found_section, start_index, end_index, velocity = get_fastest_section(5000, parser)
    assert found_section is False
    assert start_index == 0
    assert end_index == 0
    assert velocity == 0.0


@pytest.mark.parametrize("test_file", ["2020-10-25-10-54-06.fit", "2020-10-25-10-54-06.fit"])
def test_sportgems_fastest_interface__fit_file_which_cause_panic(fit_parser, test_file):
    parser = fit_parser(test_file)
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)
    for section in fastest_sections:
        found_section, _, _, _ = find_gems(int(1000 * section), times, coordinates)

        # sanity check that no section causes rust panic
        assert found_section in [True, False]
