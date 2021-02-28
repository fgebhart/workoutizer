# supported for parsing
supported_formats = {".gpx", ".fit"}

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

# configuration of best sections
rank_limit = 3

# fastest section to parse in activities (in kilometer, only integers allowed)
fastest_sections = {
    1,
    2,
    3,
    5,
    10,
}

# with respect to the table listing activities used both on dashboard and sport page
number_of_rows_per_page_in_table = 40
