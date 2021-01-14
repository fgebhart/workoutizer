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
