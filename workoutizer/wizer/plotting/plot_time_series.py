import logging
import json

import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool

from django.conf import settings

log = logging.getLogger(__name__)

plot_matrix = {
    "temperature": {
        "color": "red",
        "axis": "°C",
        "title": "Temperature",
    },
    "cadence": {
        "color": "blue",
        "axis": "steps/min",
        "title": "Cadence",
    },
    "speed": {
        "color": "black",
        "axis": "m/s",
        "title": "Speed",
    },
    "heart_rate": {
        "color": "green",
        "axis": "bpm",
        "title": "Heart Rate",
    },
}


def plot_time_series(activity):
    dict_containing_divs_and_scripts = {}
    attributes = activity.trace_file.__dict__
    del attributes["coordinates_list"]
    del attributes["altitude_list"]
    del attributes["timestamps_list"]
    for attribute, values in attributes.items():
        if attribute.endswith("_list"):
            values = json.loads(values)
            if values:
                attribute = attribute.replace("_list", "")
                x_axis = np.arange(0, activity.distance, activity.distance / len(values))
                p = figure(plot_height=int(settings.PLOT_HEIGHT / 2),
                           sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"])
                p.tools = []
                p.toolbar.logo = None
                p.toolbar_location = None
                if attribute == 'cadence':
                    p.scatter(x_axis, values, radius=0.01, fill_alpha=1, color=plot_matrix[attribute]["color"])
                else:
                    p.line(x_axis, values, line_width=2, color=plot_matrix[attribute]["color"])
                hover = HoverTool(
                    tooltips=[(plot_matrix[attribute]['title'], f"@y {plot_matrix[attribute]['axis']}")],
                    mode='vline')
                p.add_tools(hover)
                p.toolbar.logo = None
                p.title.text = plot_matrix[attribute]["title"]
                p.xaxis[0].ticker.desired_num_ticks = 10

                script, div = components(p)
                name = attribute.replace("_", " ").title()
                dict_containing_divs_and_scripts[name] = {"script": script, "div": div}

    return dict_containing_divs_and_scripts
