import datetime
import logging

import pandas as pd
from bokeh.embed import components
from bokeh.models import FuncTickFormatter, HoverTool, LinearAxis, Range1d
from bokeh.plotting import figure

from wkz import models
from wkz.tools.style import Style

log = logging.getLogger(__name__)


def plot_workload(activity_model: models.Activity):
    df = pd.DataFrame(list(activity_model.objects.all().values("distance", "duration", "date")))

    duration_df = df[["date", "duration"]]
    distance_df = df[["date", "distance"]]

    first_date = df["date"].dt.tz_localize(None).min()
    time_diff_since_fist_date = pd.Timestamp(datetime.datetime.now()) - first_date
    aggregated_by = _determine_grouping_invterval(time_diff_since_fist_date)

    if aggregated_by == "Weeks":
        df = duration_df.groupby(pd.Grouper(freq="W", key="date")).sum().reset_index().sort_values("date")
        df["distance"] = (
            distance_df.groupby(pd.Grouper(freq="W", key="date")).sum().reset_index().sort_values("date")["distance"]
        )
        del distance_df
        del duration_df
        g = df.groupby(pd.Grouper(freq="W", key="date"))["date"]
        df["week_begin"] = g.transform("first").dt.date
        df["week_end"] = df["week_begin"] + pd.Timedelta(days=7)
        df["x_axis_formatted"] = df["week_begin"].astype(str) + " - " + df["week_end"].astype(str)
    elif aggregated_by == "Months":
        df = duration_df.groupby(pd.Grouper(freq="M", key="date")).sum().reset_index().sort_values("date")
        df["distance"] = (
            distance_df.groupby(pd.Grouper(freq="M", key="date")).sum().reset_index().sort_values("date")["distance"]
        )
        del distance_df
        del duration_df
        g = df.groupby(pd.Grouper(freq="M", key="date"))["date"]
        df["x_axis_formatted"] = (
            g.transform("first").dt.month_name().astype(str) + " " + g.transform("first").dt.year.astype(str)
        )
    df["x_axis"] = g.transform("first").dt.date

    df.drop(columns="date", inplace=True)
    df["duration_formatted"] = df["duration"].dt.to_pytimedelta().astype(str)

    p = figure(
        height=200,
        toolbar_location=None,
        sizing_mode="stretch_width",
        x_axis_type="datetime",
    )
    p.tools = []
    p.y_range.start = 0

    # First line: Duration
    p.line(
        "x_axis",
        "duration",
        line_width=3,
        color=Style.colors.theme_colors.red,
        legend_label="Duration",
        source=df,
    )

    # First line: Distance
    y_column2_range = "y2_range"

    distance_line = p.line(
        "x_axis",
        "distance",
        line_width=3,
        y_range_name=y_column2_range,
        color=Style.colors.theme_colors.green,
        legend_label="Distance",
        source=df,
    )

    # show duration (timedelta) y-axis in hours instead of milliseconds
    p.yaxis.formatter = FuncTickFormatter(code="return parseInt(tick / 3600 / 1000)")
    p.yaxis.major_label_text_font = Style.font
    p.xaxis.major_label_text_font = Style.font
    p.yaxis.axis_label = "Duration [h]"
    p.yaxis.axis_label_text_font = Style.font
    p.yaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_standoff = 10
    p.extra_y_ranges = {
        y_column2_range: Range1d(
            start=None,
            end=df["distance"].max(),
        )
    }
    p.add_layout(
        LinearAxis(
            y_range_name=y_column2_range,
            major_label_text_font=Style.font,
            minor_tick_line_color=None,
            axis_label_text_font=Style.font,
            axis_label="Distance [km]",
            axis_label_text_font_style="normal",
            axis_label_standoff=10,
        ),
        "right",
    )
    p.xgrid.grid_line_color = None
    p.add_tools(
        HoverTool(
            tooltips=[
                (aggregated_by[:-1], "@x_axis_formatted"),
                ("Duration", "@duration_formatted h"),
                ("Distance", "@distance km"),
            ],
            mode="vline",
            renderers=[distance_line],
        )
    )
    p.legend.label_text_font = Style.font
    p.legend.location = "top_left"
    script, div = components(p)

    return script, div, aggregated_by


def _determine_grouping_invterval(time_diff: pd.Timedelta) -> str:
    if time_diff > pd.Timedelta(weeks=20):
        aggregated_by = "Months"
    else:
        aggregated_by = "Weeks"
    log.debug(f"aggregating data for workload plot by: {aggregated_by}")
    return aggregated_by
