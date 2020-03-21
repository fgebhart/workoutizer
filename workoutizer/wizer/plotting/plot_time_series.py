import logging
import json
import datetime

import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components

from django.conf import settings
from wizer.tools.utils import ensure_list_have_same_length

log = logging.getLogger(__name__)

plot_matrix = {
    "temperature": {
        "color": "red",
        "axis": "[°C]",
        "title": "Temperature",
    },
    "cadence": {
        "color": "blue",
        "axis": "[steps/min]",
        "title": "Cadence",
    },
    "speed": {
        "color": "black",
        "axis": "[m/s]",
        "title": "Speed",
    },
    "heart_rate": {
        "color": "green",
        "axis": "[beats/min]",
        "title": "Heart Rate",
    },
}


def plot_time_series(activity):
    dict_containing_divs_and_scripts = {}
    attributes = activity.trace_file.__dict__
    del attributes["coordinates_list"]
    del attributes["altitude_list"]
    timestamps_list = json.loads(attributes.pop("timestamps_list"))
    # time_axis = np.array(timestamps_list, dtype='i8').view('datetime64[ms]').tolist()
    time_axis = [datetime.datetime.fromtimestamp(t) for t in timestamps_list]
    # time_axis = pd.to_datetime(timestamps_list)
    for attribute, values in attributes.items():
        if attribute.endswith("_list"):
            values = json.loads(values)
            if values:
                attribute = attribute.replace("_list", "")
                time_axis, values = ensure_list_have_same_length(time_axis, values)
                p = figure(x_axis_type='datetime', plot_height=int(settings.PLOT_HEIGHT/2),
                           sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"])
                p.scatter(time_axis, values, radius=5000, fill_alpha=1, color=plot_matrix[attribute]["color"])
                p.title.text = plot_matrix[attribute]["title"]
                p.toolbar.logo = None
                p.tools = []

                script, div = components(p)
                name = attribute.replace("_", " ").title()
                dict_containing_divs_and_scripts[name] = {"script": script, "div": div}

    return dict_containing_divs_and_scripts
