from sportgems import find_best_climb_section

from wizer.best_sections.generic import GenericBestSection


def get_best_climb_section(section_distance: int, parser) -> GenericBestSection:
    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    # safety check to catch activities with empty altitude list
    if not parser.altitude_list:
        return None

    # call to rust
    section = find_best_climb_section(
        desired_distance=section_distance,
        times=parser.timestamps_list,
        coordinates=coordinates,
        altitudes=parser.altitude_list,
    )

    return GenericBestSection(
        start=section.start,
        end=section.end,
        distance=section_distance,
        max_value=round(section.climb, 2),
        kind="climb",
    )
