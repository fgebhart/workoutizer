from wizer.best_sections.fastest import get_fastest_section
from wizer.best_sections.climb import get_best_climb_section


# supported for parsing
supported_formats = {"gpx", "fit"}

# cannot be edited nor deleted
protected_sports = {"unknown"}

# all time series attributes
time_series_attributes = {
    "latitude_list",
    "longitude_list",
    "timestamps_list",
    "distance_list",
    "heart_rate_list",
    "altitude_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
}

# will create a time series plot for these list attributes
attributes_to_create_time_series_plot_for = {
    "heart_rate_list",
    "altitude_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
}

min_max_attributes = {
    "heart_rate_list",
    "altitude_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
}

avg_attributes = {
    "heart_rate_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
}

# configuration of best sections
rank_limit = 3

# best sections config
best_sections = [
    {
        "kind": "fastest",
        "parser": get_fastest_section,
        "distances": [  # in meter
            1_000,
            2_000,
            3_000,
            5_000,
            10_000,
        ],
    },
    {
        "kind": "climb",
        "parser": get_best_climb_section,
        "distances": [  # in meter
            100,
            200,
            500,
            1_000,
            2_000,
        ],
    },
]
available_best_section = [sec["kind"] for sec in best_sections]
fastest_distances = best_sections[0]["distances"]
climb_distances = best_sections[1]["distances"]

# with respect to the table listing activities used both on dashboard and sport page
number_of_rows_per_page_in_table = 40
