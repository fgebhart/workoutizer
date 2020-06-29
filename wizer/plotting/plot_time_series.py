import logging
import json

import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.models import CheckboxButtonGroup, CustomJS, Button
from bokeh.layouts import column

from django.conf import settings
from wizer.tools.utils import ensure_lists_have_same_length, timestamp_to_local_time
from wizer.models import Lap

log = logging.getLogger(__name__)

plot_matrix = {
    "temperature": {
        "color": "OrangeRed",
        "axis": "°C",
        "title": "Temperature",
    },
    "cadence": {
        "color": "MediumSlateBlue",
        "axis": "revolutions/min",
        "title": "Cadence",
    },
    "speed": {
        "color": "darkred",
        "axis": "m/s",
        "title": "Speed",
    },
    "heart_rate": {
        "color": "DarkOrange",
        "axis": "bpm",
        "title": "Heart Rate",
    },
}


def plot_time_series(activity):
    attributes = activity.trace_file.__dict__
    del attributes["coordinates_list"]
    del attributes["altitude_list"]
    lap_data = Lap.objects.filter(trace=activity.trace_file, trigger='manual')
    plots = []
    lap_lines = []

    for attribute, values in attributes.items():
        if attribute.endswith("_list") and attribute != 'timestamps_list':
            values = json.loads(values)
            if values:
                attribute = attribute.replace("_list", "")
                if activity.distance:
                    x_axis = np.arange(0, activity.distance, activity.distance / len(values))
                    p = figure(plot_height=int(settings.PLOT_HEIGHT / 2),
                               sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"],
                               x_range=(0, x_axis[-1]))
                    lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values)
                else:  # activity has no distance data, use time for x-axis instead
                    timestamps_list = json.loads(attributes["timestamps_list"])
                    start = timestamp_to_local_time(timestamps_list[0])
                    x_axis = [timestamp_to_local_time(t) - start for t in timestamps_list]
                    x_axis, values = ensure_lists_have_same_length(x_axis, values)
                    p = figure(x_axis_type='datetime', plot_height=int(settings.PLOT_HEIGHT / 2),
                               sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"])
                    lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values,
                                            x_start_value=x_axis[0], use_time=True)
                lap_lines += lap
                p.tools = []
                p.toolbar.logo = None
                p.toolbar_location = None
                p.xgrid.grid_line_color = None
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
                plots.append(p)

    # TODO
    # connect all plots and share hovering line
    # add hover info for each lap line with lap data info
    all_plots = column(*plots)
    all_plots.sizing_mode = "stretch_width"

    if lap_data:
        log.debug(f"found some Lap data for {activity}: {lap_data}")
        checkbox = CheckboxButtonGroup(labels=["Show Laps"], active=[0], width=100)

        js = """
            for (line in laps) {
                laps[line].visible = false;
                markerGroup.removeFrom(map);
            }
            for (i in cb_obj.active) {
                if (cb_obj.active[i] == 0) {
                    for (line in laps) {
                        laps[line].visible = true;
                        markerGroup.addTo(map);
                    }
                }
            }
        """
        callback = CustomJS(args=dict(laps=lap_lines, checkbox=checkbox), code=js)
        checkbox.js_on_change('active', callback)
        layout = column(checkbox, all_plots)
        layout.sizing_mode = 'stretch_width'
        script, div = components(layout)
    else:
        script, div = components(all_plots)

    return script, div


def _add_laps_to_plot(laps: list, plot, y_values: list, x_start_value: int = 0, use_time: bool = False):
    lap_lines = []
    for lap in laps:
        if use_time:
            x_start_value = lap.elapsed_time
        else:
            x_start_value += lap.distance / 1000
        line = plot.line([x_start_value, x_start_value], [min(y_values) - 1, max(y_values) + 1], color='grey')

        if lap.trigger == 'manual':
            lap_lines.append(line)
    return lap_lines
