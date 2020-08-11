import logging
import json
from itertools import combinations

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, CrosshairTool
from bokeh.models import CheckboxButtonGroup, CustomJS
from bokeh.layouts import column

from django.conf import settings
from wizer.tools.utils import cut_list_to_have_same_length, timestamp_to_local_time, extend_list_to_have_length, \
    convert_list_to_km
from wizer.naming import attributes_to_create_time_series_plot_for
from wizer import models


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
    "altitude": {
        "color": "Green",
        "second_color": "darkseagreen",
        "axis": "m",
        "title": "Altitude",
    }
}


def plot_time_series(activity: models.Activity):
    """
    Plotting function to create the time series plots shown in tha activity page. Depending
    on what data is available this creates the following plots:
    - Altitude
    - Heart Rate
    - Speed
    - Cadence
    - Temperature
    All plots share a connected vertical cross hair tools.

    Parameters
    ----------
    activity : models.Activity
        Activity model containing the required activity for which the plots should be generated

    Returns
    -------
    script, div : tuple(str, str)
        the html script and div elements used to render the plots in the html templates
    """

    attributes = activity.trace_file.__dict__
    coordinates = json.loads(attributes["coordinates_list"])
    initial_list_of_distances = []
    list_of_distances = []
    if coordinates:
        initial_list_of_distances = convert_list_to_km(json.loads(attributes['distance_list']))
        list_of_distances = extend_list_to_have_length(length=len(coordinates), input_list=initial_list_of_distances)

    lap_data = models.Lap.objects.filter(trace=activity.trace_file)
    plots = []
    lap_lines = []

    for attribute, values in attributes.items():
        if attribute in attributes_to_create_time_series_plot_for:
            values = json.loads(values)
            if values:
                attribute = attribute.replace("_list", "")
                if activity.distance:
                    x_axis = extend_list_to_have_length(length=len(values), input_list=initial_list_of_distances)
                    p = figure(plot_height=int(settings.PLOT_HEIGHT / 2.5),
                               sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"],
                               x_range=(0, x_axis[-1]))
                    lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values)
                    x_hover = ("Distance", "@x km")
                else:  # activity has no distance data, use time for x-axis instead
                    timestamps_list = json.loads(attributes["timestamps_list"])
                    start = timestamp_to_local_time(timestamps_list[0])
                    x_axis = [timestamp_to_local_time(t) - start for t in timestamps_list]
                    x_axis, values = cut_list_to_have_same_length(x_axis, values)
                    p = figure(x_axis_type='datetime', plot_height=int(settings.PLOT_HEIGHT / 2.5),
                               sizing_mode='stretch_width', y_axis_label=plot_matrix[attribute]["axis"])
                    lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values,
                                            x_start_value=x_axis[0], use_time=True)
                    x_hover = ("Time", "@x")
                lap_lines += lap
                p.toolbar.logo = None
                p.toolbar_location = None
                p.xgrid.grid_line_color = None
                if attribute == 'cadence':
                    p.scatter(x_axis, values, radius=0.01, fill_alpha=1, color=plot_matrix[attribute]["color"],
                              legend_label=plot_matrix[attribute]["title"])
                elif attribute == 'altitude':
                    p.varea(x_axis, values, [min(values) for i in range(len(values))],
                            color=plot_matrix[attribute]["second_color"], fill_alpha=0.5)
                    p.line(x_axis, values, line_width=2, color=plot_matrix[attribute]["color"],
                           legend_label=plot_matrix[attribute]["title"])
                else:
                    p.line(x_axis, values, line_width=2, color=plot_matrix[attribute]["color"],
                           legend_label=plot_matrix[attribute]["title"])
                hover = HoverTool(
                    tooltips=[(plot_matrix[attribute]['title'], f"@y {plot_matrix[attribute]['axis']}"),
                              x_hover],
                    mode='vline')
                p.add_tools(hover)
                cross = CrosshairTool(dimensions="height")
                p.add_tools(cross)
                p.legend.location = "top_left"
                p.legend.label_text_font = "ubuntu"
                p.legend.background_fill_alpha = 0.9
                plots.append(p)

    _link_all_plots_with_each_other(all_plots=plots, x_values=list_of_distances)

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
                if (typeof markerGroup != "undefined") {
                    markerGroup.removeFrom(map);
                    }
            }
            for (i in cb_obj.active) {
                if (cb_obj.active[i] == 0) {
                    for (line in laps) {
                        laps[line].visible = true;
                        if (typeof markerGroup != "undefined") {
                            markerGroup.addTo(map);
                            }
                    }
                }
            }
        """
        callback = CustomJS(args=dict(laps=lap_lines, checkbox=checkbox), code=js)
        checkbox.js_on_change('active', callback)
        layout = column(all_plots, checkbox)
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
        if lap.trigger == 'manual':
            line = plot.line([x_start_value, x_start_value], [min(y_values) - 1, max(y_values) + 1], color='grey')
            lap_lines.append(line)
    return lap_lines


def _add_vlinked_crosshairs(fig1, fig2, x_values):
    cross1 = CrosshairTool(dimensions="height")
    cross2 = CrosshairTool(dimensions="height")
    fig1.add_tools(cross1)
    fig2.add_tools(cross2)
    js_move = '''
        if(cb_obj.x >= fig.x_range.start && cb_obj.x <= fig.x_range.end &&
           cb_obj.y >= fig.y_range.start && cb_obj.y <= fig.y_range.end)
        {
            cross.spans.height.computed_location = cb_obj.sx
            
            // determine closest point in list of x_values in order to render 
            // the current position when hovering over time series plots
            var closest = x_values.reduce(function (prev, curr) {
                return (Math.abs(curr - cb_obj.x) < Math.abs(prev - cb_obj.x) ? curr : prev);
            });
            var index = x_values.indexOf(closest);
            
            // call rendering function, defined in activity_map.html
            render_position(index);
        }
        else
        {
            cross.spans.height.computed_location = null
        }
    '''
    js_leave = 'cross.spans.height.computed_location = null'
    args = {'cross': cross2, 'fig': fig1, "x_values": x_values}
    fig1.js_on_event('mousemove', CustomJS(args=args, code=js_move))
    fig1.js_on_event('mouseleave', CustomJS(args=args, code=js_leave))
    args = {'cross': cross1, 'fig': fig2, "x_values": x_values}
    fig2.js_on_event('mousemove', CustomJS(args=args, code=js_move))
    fig2.js_on_event('mouseleave', CustomJS(args=args, code=js_leave))


def _link_all_plots_with_each_other(all_plots: list, x_values: list):
    for combi in combinations(all_plots, 2):
        _add_vlinked_crosshairs(combi[0], combi[1], x_values=x_values)
