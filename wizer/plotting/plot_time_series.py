import json
from itertools import combinations
from typing import List, Tuple

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import CheckboxButtonGroup, CustomJS, HoverTool, CrosshairTool, BoxZoomTool
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.layouts import column, gridplot
import pandas as pd

from django.conf import settings
from wizer.configuration import attributes_to_create_time_series_plot_for
from wizer import models


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
        "axis": "km/h",
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
    },
}


def plot_time_series(activity: models.Activity) -> Tuple[str, str]:
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
    lap_data = models.Lap.objects.filter(trace=activity.trace_file)
    plots = []
    lap_lines = []

    timestamps = pd.to_datetime(pd.Series(json.loads(attributes["timestamps_list"]), dtype=float), unit="s")
    x_axis = pd.to_datetime(timestamps).dt.tz_localize("utc").dt.tz_convert(settings.TIME_ZONE)
    x_axis = x_axis - x_axis.min()

    box_zoom_tool = BoxZoomTool(dimensions="width")
    for attribute, values in attributes.items():
        if attribute in attributes_to_create_time_series_plot_for:
            values = pd.Series(json.loads(values), dtype=float)
            if values.any():
                attribute = attribute.replace("_list", "")

                p = figure(
                    x_axis_type="datetime",
                    plot_height=int(settings.PLOT_HEIGHT / 2.5),
                    sizing_mode="stretch_width",
                    y_axis_label=plot_matrix[attribute]["axis"],
                    tools="reset",
                )

                if attribute == "speed":
                    # turn speed values from m/s into km/h to be consistent with other speed values
                    values = values.mul(3.6)
                if attribute == "altitude":
                    p.varea(
                        x=x_axis,
                        y1=values,
                        y2=values.min(),
                        color=plot_matrix[attribute]["second_color"],
                        fill_alpha=0.5,
                    )
                    p.line(
                        x_axis,
                        values,
                        line_width=2,
                        color=plot_matrix[attribute]["color"],
                        legend_label=plot_matrix[attribute]["title"],
                    )
                else:
                    p.line(
                        x_axis,
                        values,
                        line_width=2,
                        color=plot_matrix[attribute]["color"],
                        legend_label=plot_matrix[attribute]["title"],
                    )

                # render vertical lap lines
                lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values)
                lap_lines += lap

                # add tools to plot
                x_hover = ("Time", "@x")
                hover = HoverTool(
                    tooltips=[(plot_matrix[attribute]["title"], f"@y {plot_matrix[attribute]['axis']}"), x_hover],
                    mode="vline",
                    toggleable=False,
                )
                p.add_tools(hover)
                p.add_tools(box_zoom_tool)

                p.xgrid.grid_line_color = None
                p.legend.location = "top_left"
                p.legend.label_text_font = "ubuntu"
                p.legend.background_fill_alpha = 0.7
                dtf = DatetimeTickFormatter()
                dtf.minutes = ["%M:%S"]
                p.xaxis.formatter = dtf
                p.xaxis.major_label_overrides = {0: "0:00"}
                plots.append(p)

                values.ffill(inplace=True)
                values.bfill(inplace=True)
                x_axis.ffill(inplace=True)
                x_axis.bfill(inplace=True)

    _link_plot_tools(all_plots=plots, x_values=x_axis)

    layout = gridplot(
        plots, sizing_mode="stretch_width", toolbar_location="right", ncols=1, toolbar_options={"logo": None}
    )

    if lap_data:
        layout = _add_button_to_toggle_laps(lap_lines, layout)

    script, div = components(layout)
    return script, div


def _add_button_to_toggle_laps(lap_lines, layout):
    # include button to toggle rendering of laps
    btn = CheckboxButtonGroup(labels=["Show Laps"], active=[0], width=100)

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
    callback = CustomJS(args={"laps": lap_lines, "checkbox": btn}, code=js)
    btn.js_on_change("active", callback)
    layout = column(layout, btn)
    layout.sizing_mode = "stretch_width"
    return layout


def _add_laps_to_plot(laps: list, plot, y_values: list) -> List:
    lap_lines = []
    x_value = pd.Timedelta(seconds=0)
    for lap in laps:
        x_value += lap.elapsed_time
        if lap.trigger == "manual":
            line = plot.line([x_value, x_value], [y_values.min() - 1, y_values.max() + 1], color="grey")
            lap_lines.append(line)
    return lap_lines


def _link_crosshair_and_render_icon_on_map_on_hover(fig1, fig2, x_values):
    cross1 = CrosshairTool(dimensions="height", toggleable=False)
    fig1.add_tools(cross1)
    fig2.add_tools(cross1)

    # js for rendering the sport icon on leaflet map when hovering over bokeh time series plots
    js_move = """
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
    """
    js_leave = "cross.spans.height.computed_location = null"
    args = {"cross": cross1, "fig": fig1, "x_values": x_values}
    fig1.js_on_event("mousemove", CustomJS(args=args, code=js_move))
    fig1.js_on_event("mouseleave", CustomJS(args=args, code=js_leave))
    args = {"cross": cross1, "fig": fig2, "x_values": x_values}
    fig2.js_on_event("mousemove", CustomJS(args=args, code=js_move))
    fig2.js_on_event("mouseleave", CustomJS(args=args, code=js_leave))


def _link_plot_tools(all_plots: list, x_values: list):
    if len(all_plots) == 1:
        _link_crosshair_and_render_icon_on_map_on_hover(all_plots[0], all_plots[0], x_values=x_values)
    else:
        for combi in combinations(all_plots, 2):
            _link_crosshair_and_render_icon_on_map_on_hover(combi[0], combi[1], x_values=x_values)
            # add x axis range for linking effect of box zoom tool
            combi[0].x_range = combi[1].x_range
