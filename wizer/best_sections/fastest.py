from typing import List, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sportgems import find_fastest_section


@dataclass
class FastestSection:
    section_distance: int
    start_index: int
    end_index: int
    max_value: float
    section_type: str = "fastest"


def _prepare_coordinates_and_times_for_fastest_secions(parser) -> Tuple[List[float], List[Tuple[float]]]:
    lat_lon_times_df = pd.DataFrame(
        {
            "times": parser.timestamps_list,
            "lon": parser.longitude_list,
            "lat": parser.latitude_list,
        }
    ).dropna()

    times = lat_lon_times_df["times"].tolist()
    coordinates = list(zip(lat_lon_times_df["lat"].tolist(), lat_lon_times_df["lon"].tolist()))
    assert len(times) == len(coordinates)
    return times, coordinates


def get_fastest_section(section_distance: int, parser) -> Tuple[float, int, int]:
    if not parser.latitude_list:
        # in case no coordinate data is available, return False and Nulls to safeguard against failures
        return False, np.NaN, np.NaN, np.NaN
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    # call the rust binary of sportgems here
    sec = find_fastest_section(section_distance, times, coordinates)

    return sec.valid_section, sec.start_index, sec.end_index, round(sec.velocity, 2)


def _activity_suitable_for_awards(activity) -> bool:
    if activity.evaluates_for_awards is False or activity.sport.evaluates_for_awards is False:
        return False
    else:
        return True
