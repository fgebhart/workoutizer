from dataclasses import dataclass


@dataclass
class GenericBestSection:
    distance: int
    start: int
    end: int
    max_value: float
    kind: str


def activity_suitable_for_awards(activity) -> bool:
    if activity.evaluates_for_awards is False or activity.sport.evaluates_for_awards is False:
        return False
    else:
        return True
