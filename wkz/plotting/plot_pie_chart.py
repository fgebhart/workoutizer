import logging
from typing import List, Tuple

log = logging.getLogger(__name__)


def plot_pie_chart(activities) -> Tuple[List[int], List[str], List[str]]:
    sport_distribution = {}
    color_list = []
    for activity in activities:
        sport_distribution[activity.sport.name] = 0
        if activity.sport.color not in color_list:
            color_list.append(activity.sport.color)
    for activity in activities:
        if activity.sport.name in sport_distribution:
            sport_distribution[activity.sport.name] += 1

    return list(sport_distribution.values()), list(sport_distribution.keys()), color_list
