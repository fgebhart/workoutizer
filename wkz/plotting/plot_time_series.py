import json
from itertools import combinations
from typing import List, Tuple

import pandas as pd
from bokeh.embed import components
from bokeh.layouts import column, gridplot
from bokeh.models import (
    BoxZoomTool,
    CheckboxButtonGroup,
    ColumnDataSource,
    CrosshairTool,
    CustomJS,
    HoverTool,
)
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure

from wkz import configuration as cfg
from wkz import models
from wkz.tools.style import Style
from workoutizer import settings as django_settings

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


def plot_time_series(activity: models.Activity) -> Tuple[str, str, int]:
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
    script, div : tuple(str, str, int)
        the html script and div elements as str used to render the plots in the html templates
        and the third element in the tuple is the number of plots to be rendered
    """

    attributes = activity.trace_file.__dict__
    lap_data = models.Lap.objects.filter(trace=activity.trace_file)
    plots = []
    lap_lines = {}

    timestamps = pd.to_datetime(
        pd.Series(json.loads(attributes["timestamps_list"]), dtype=float).iloc[:: cfg.every_nth_value], unit="s"
    )
    x_axis = pd.to_datetime(timestamps).dt.tz_localize("utc").dt.tz_convert(django_settings.TIME_ZONE)
    x_axis = x_axis - x_axis.min()
    source = ColumnDataSource(data={"x_axis": x_axis, "x_formatted": x_axis.dt.to_pytimedelta().astype(str)})

    box_zoom_tool = BoxZoomTool(dimensions="width")
    for y_axis, values in attributes.items():
        if y_axis in cfg.attributes_to_create_time_series_plot_for:
            values = pd.Series(json.loads(values), dtype=float).iloc[:: cfg.every_nth_value]
            y_axis = y_axis.replace("_list", "")
            if values.any():
                if y_axis == "speed":
                    # turn speed values from m/s into km/h to be consistent with other speed values
                    values = values.mul(3.6)

                # add current values to plotting source data
                source.add(values, y_axis)

                p = figure(
                    plot_height=int(django_settings.PLOT_HEIGHT / 2.5),
                    sizing_mode="stretch_width",
                    y_axis_label=plot_matrix[y_axis]["axis"],
                    tools="reset",
                )

                if y_axis == "altitude":
                    p.varea(
                        x="x_axis",
                        y1=y_axis,
                        y2=values.min(),
                        color=plot_matrix[y_axis]["second_color"],
                        fill_alpha=0.5,
                        source=source,
                    )
                    p.line(
                        x="x_axis",
                        y=y_axis,
                        line_width=2,
                        color=plot_matrix[y_axis]["color"],
                        legend_label=plot_matrix[y_axis]["title"],
                        source=source,
                    )
                else:
                    p.line(
                        x="x_axis",
                        y=y_axis,
                        line_width=2,
                        color=plot_matrix[y_axis]["color"],
                        legend_label=plot_matrix[y_axis]["title"],
                        source=source,
                    )

                # render vertical lap lines
                lap = _add_laps_to_plot(laps=lap_data, plot=p, y_values=values)
                for trigger, line in lap.items():
                    if trigger not in lap_lines:
                        lap_lines[trigger] = []
                    lap_lines[trigger] = lap_lines[trigger] + line

                # add tools to plot
                digits = "{0.0}"
                hover = HoverTool(
                    tooltips=[
                        (plot_matrix[y_axis]["title"], f"@{y_axis}{digits} " + plot_matrix[y_axis]["axis"]),
                        ("Time", "@x_formatted"),
                    ],
                    mode="vline",
                    toggleable=False,
                )
                p.add_tools(hover)
                p.add_tools(box_zoom_tool)

                p.xgrid.grid_line_color = None
                p.legend.location = "top_left"
                p.legend.label_text_font = Style.font
                p.legend.background_fill_alpha = 0.7
                p.yaxis.major_label_text_font = Style.font
                p.xaxis.major_label_text_font = Style.font
                p.yaxis.axis_label_text_font = Style.font
                p.yaxis.axis_label_text_font_style = "normal"
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
    return script, div, len(plots)


def _add_button_to_toggle_laps(lap_lines, layout):
    # include button to toggle rendering of laps
    btn = CheckboxButtonGroup(labels=["Show Auto Laps", "Show Manual Laps"], active=[1], width=100)

    js = """
        function ChangeLapLineState(laps, state) {
            for (line in laps) {
                laps[line].visible = state;
            }
        }

        function ChangeAutoLapLineState(laps, state) {
            autolap_triggers = ["time",
                            "distance",
                            "position_start",
                            "position_lap",
                            "position_waypoint",
                            "position_marked"]
            for (type in autolap_triggers) {
                ChangeLapLineState(laps[autolap_triggers[type]], state)
            }
        }

        for (types in laps) {
            if (typeof autoLapGroup != "undefined") {
               autoLapGroup.removeFrom(map);
               manualLapGroup.removeFrom(map);
            }
            ChangeLapLineState(laps[types], false)
        }

        for (i in cb_obj.active) {
            if (cb_obj.active[i] == 0) {
                if (typeof autoLapGroup != "undefined") {
                    autoLapGroup.addTo(map);
                }
                ChangeAutoLapLineState(laps, true)
            }
            if (cb_obj.active[i] == 1) {
                if (typeof manualLapGroup != "undefined") {
                    manualLapGroup.addTo(map);
                }
                ChangeLapLineState(laps['manual'], true)
            }
        }
        """
    callback = CustomJS(args={"laps": lap_lines, "checkbox": btn}, code=js)
    btn.js_on_change("active", callback)
    layout = column(layout, btn)
    layout.sizing_mode = "stretch_width"
    return layout


def _add_laps_to_plot(laps: list, plot, y_values: list) -> List:
    lap_lines = {}
    colors = Style.colors
    lap_colors = {
        "manual": colors.lap_colors.manual,
        "time": colors.lap_colors.time,
        "distance": colors.lap_colors.distance,
        "position_start": colors.lap_colors.position_start,
        "position_lap": colors.lap_colors.position_lap,
        "position_waypoint": colors.lap_colors.position_waypoint,
        "position_marked": colors.lap_colors.position_marked,
        "session_end": colors.lap_colors.session_end,
        "fitness_equipment": colors.lap_colors.fitness_equipment,
    }
    x_value = pd.Timedelta(seconds=0)
    for lap in laps:
        x_value += lap.elapsed_time
        if lap.trigger not in ("unknown", "session_end"):
            if lap.trigger == "manual":
                visible = True
            else:
                visible = False
            line = plot.line(
                [x_value, x_value],
                [y_values.min() - 1, y_values.max() + 1],
                color=lap_colors[lap.trigger],
                visible=visible,
            )
            if lap.trigger not in lap_lines:
                lap_lines[lap.trigger] = []
            lap_lines[lap.trigger].append(line)
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
