import logging
import json

import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components

from django.conf import settings

log = logging.getLogger(__name__)


def plot_time_series(activity):
    dict_containing_divs_and_scripts = {}
    attributes = activity.trace_file.__dict__
    del attributes["coordinates_list"]
    del attributes["altitude_list"]
    # timestamps_list = attributes.pop("timestamps_list")
    for attribute, value in attributes.items():
        if attribute.endswith("_list"):
            value = json.loads(value)
            print(f"attribute: {attribute}, len of value: {len(value)}")  # , value: {value}")
            p = figure(x_axis_type='datetime', y_axis_type='datetime', plot_height=int(settings.PLOT_HEIGHT/2),
                       sizing_mode='stretch_width')
            N = 40
            x = np.random.random(size=N) * 100
            y = np.random.random(size=N) * 100

            p.scatter(x, y, radius=0.3, fill_alpha=1, color=activity.sport.color)

            script, div = components(p)
            name = attribute.replace("_list", "").replace("_", " ").title()
            dict_containing_divs_and_scripts[name] = {"script": script, "div": div}
    return dict_containing_divs_and_scripts
