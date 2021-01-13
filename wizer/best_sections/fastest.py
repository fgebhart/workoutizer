from typing import List, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sportgems import find_gems


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
        return False, np.NaN, np.NaN, np.NaN
    times, coordinates = _prepare_coordinates_and_times_for_fastest_secions(parser)

    found_section, start_index, end_index, velocity = find_gems(section_distance, times, coordinates)

    return found_section, start_index, end_index, round(velocity, 2)
