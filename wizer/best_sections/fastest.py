from sportgems import find_fastest_section

from wizer.best_sections.generic import GenericBestSection


def get_fastest_section(distance: int, parser) -> GenericBestSection:
    # safety check to catch activities with missing coordinate data
    if not parser.latitude_list or not parser.longitude_list:
        return None

    coordinates = list(zip(parser.latitude_list, parser.longitude_list))

    # call to rust
    section = find_fastest_section(distance, parser.timestamps_list, coordinates)

    return GenericBestSection(
        start=section.start,
        end=section.end,
        distance=distance,
        max_value=round(section.velocity, 2),
        kind="fastest",
    )
