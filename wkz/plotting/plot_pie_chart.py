import logging
from math import pi

import pandas as pd
from bokeh.transform import cumsum
from bokeh.embed import components
from bokeh.plotting import figure

log = logging.getLogger(__name__)


def plot_pie_chart(activities):
    sport_distribution = {}
    color_list = []
    for activity in activities:
        try:
            sport_distribution[activity.sport.name] = 0
        except AttributeError as e:
            log.error(f"activity {activity} has unknown sport '{activity.sport}'.")
            raise e
        if activity.sport.color not in color_list:
            color_list.append(activity.sport.color)
    for activity in activities:
        if activity.sport.name in sport_distribution:
            sport_distribution[activity.sport.name] += 1

    data = pd.Series(sport_distribution).reset_index(name="value").rename(columns={"index": "country"})
    data["angle"] = data["value"] / data["value"].sum() * 2 * pi
    data["color"] = color_list

    p = figure(
        plot_height=120,
        toolbar_location=None,
        sizing_mode="stretch_width",
        tools="hover",
        tooltips="@country: @value",
        x_range=(-0.5, 1.0),
    )

    p.wedge(
        x=0.3,
        y=0.5,
        radius=0.3,
        start_angle=cumsum("angle", include_zero=True),
        end_angle=cumsum("angle"),
        line_color="white",
        fill_color="color",
        source=data,
    )

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None
    p.outline_line_color = None
    p.background_fill_color = "whitesmoke"
    p.border_fill_color = "whitesmoke"

    script_pc, div_pc = components(p)

    return script_pc, div_pc
