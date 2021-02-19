# supported for parsing
supported_formats = [".gpx", ".fit"]

# cannot be edited nor deleted
protected_sports = ["unknown"]

# will create a time series plot for these list attributes
attributes_to_create_time_series_plot_for = [
    "heart_rate_list",
    "altitude_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
]

min_max_attributes = [
    "heart_rate_list",
    "altitude_list",
    "cadence_list",
    "speed_list",
    "temperature_list",
]

# configuration of best sections
rank_limit = 3

# fastest section to parse in activities (in kilometer) (only integers allowed)
fastest_sections = [
    1,
    2,
    3,
    5,
    7,
    10,
    20,
    30,
    50,
    75,
    100,
    150,
    200,
    250,
    300,
]

# with respect to the table listing activities used both on dashboard and sport page
number_of_rows_per_page_in_table = 40
