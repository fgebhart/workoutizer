from typing import List, Tuple
from dataclasses import dataclass

import numpy as np
from sportgems import find_fastest_section


@dataclass
class FastestSection:
    section_distance: int
    start_index: int
    end_index: int
    max_value: float
    section_type: str = "fastest"


def _prepare_coordinates_and_times_for_fastest_secions(parser) -> Tuple[List[float], List[Tuple[float]]]:
    times = parser.timestamps_list
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))
    assert len(times) == len(coordinates)
    return times, coordinates


def get_fastest_section(section_distance: int, parser) -> Tuple[float, int, int]:
    if not parser.latitude_list:
        # in case no coordinate data is available, return False and Nulls to safeguard against failures
        return False, np.NaN, np.NaN, np.NaN
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    # call the rust binary of sportgems here
    return find_fastest_section(section_distance, times, coordinates)


def _activity_suitable_for_awards(activity) -> bool:
    if activity.evaluates_for_awards is False or activity.sport.evaluates_for_awards is False:
        return False
    else:
        return True
