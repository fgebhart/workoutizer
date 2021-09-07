from dataclasses import dataclass

from bokeh.palettes import Set1, Set2_8


@dataclass
class ThemeColors:
    yellow = "#FCC468"
    red = "#F17E5D"
    green = "#6BD098"
    blue = "#51CBCE"


@dataclass
class LapColors:
    time = Set2_8[1]
    distance = Set2_8[3]
    manual = Set2_8[0]
    position_start = Set2_8[2]
    position_lap = Set2_8[2]
    position_waypoint = Set2_8[2]
    position_marked = Set2_8[2]
    fitness_equipment = Set2_8[4]
    session_end = Set2_8[6]


@dataclass
class DemoSportColors:
    hiking = ThemeColors.green
    swimming = ThemeColors.blue
    cycling = ThemeColors.yellow
    jogging = ThemeColors.red


@dataclass
class Colors:
    lap_colors = LapColors
    demo_sport_colors = DemoSportColors
    theme_colors = ThemeColors


# color of traces rendered on map in sport page
sport_trace_colors = Set1[9]
