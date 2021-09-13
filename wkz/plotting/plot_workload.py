import datetime
import logging

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter, HoverTool, LinearAxis, Range1d
from bokeh.plotting import figure
from bokeh.transform import dodge

from wkz import models
from wkz.tools.style import Set1Palette, Style

BAR_WIDTH = 0.45
BAR_DODGE = 0.15


log = logging.getLogger(__name__)


def plot_workload(activity_model: models.Activity):
    df = pd.DataFrame(list(activity_model.objects.all().values("distance", "duration", "date")))

    duration_df = df[["date", "duration"]]
    distance_df = df[["date", "distance"]]

    # TODO: figure out at what conditions to group by week and when to group by months
    # always show at maximum 20 twin-vbars
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
        df["x_axis"] = g.transform("first").dt.strftime("%m/%d")
        df["x_axis_formatted"] = df["week_begin"].astype(str) + " - " + df["week_end"].astype(str)
    elif aggregated_by == "Months":
        df = duration_df.groupby(pd.Grouper(freq="M", key="date")).sum().reset_index().sort_values("date")
        df["distance"] = (
            distance_df.groupby(pd.Grouper(freq="M", key="date")).sum().reset_index().sort_values("date")["distance"]
        )
        del distance_df
        del duration_df
        g = df.groupby(pd.Grouper(freq="M", key="date"))["date"]
        # df["month_begin"] = g.transform("first").dt.date
        # df["month_end"] = df["month_begin"] + pd.Timedelta(days=7)
        df["x_axis"] = g.transform("first").dt.strftime("%Y/%m")
        df["x_axis_formatted"] = (
            g.transform("first").dt.month_name().astype(str) + " " + g.transform("first").dt.year.astype(str)
        )

    df.drop(columns="date", inplace=True)
    df["duration_formatted"] = df["duration"].dt.to_pytimedelta().astype(str)  # TODO always show hours, not days
    x_axis = np.sort(df["x_axis"].unique())

    p = figure(
        height=200,
        x_range=x_axis,
        toolbar_location=None,
        sizing_mode="stretch_width",
        # y_axis_type="datetime",
    )
    p.tools = []
    p.y_range.start = 0

    # yaxis = p.select(dict(type=Axis, layout="left"))[0]
    # yaxis.formatter.use_scientific = False
    # TODO manage to show hours and not nanoseconds or whatever it is
    p.yaxis.formatter = DatetimeTickFormatter(
        days="%H:%M",
        months="%H:%M",
        hours="%H:%M",
        minutes="%H:%M",
    )

    p.vbar(
        x=dodge("x_axis", -BAR_DODGE, range=p.x_range),
        top="duration",
        width=BAR_WIDTH,
        source=df,
        fill_color=Set1Palette.orange,
        line_color=Set1Palette.orange,
        legend_label="Aggregated Duration",
    )
    p.yaxis.major_label_overrides = {0: "0h"}
    p.yaxis.major_label_text_font = Style.font
    p.xaxis.major_label_text_font = Style.font
    p.yaxis.axis_label = "Duration [h]"
    p.yaxis.axis_label_text_font = Style.font
    p.yaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_standoff = 10
    y_column2 = "y2"
    y_column2_range = y_column2 + "_range"
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

    p.vbar(
        x=dodge("x_axis", BAR_DODGE, range=p.x_range),
        top="distance",
        width=BAR_WIDTH,
        source=df,
        fill_color=Set1Palette.violet,
        line_color=Set1Palette.violet,
        legend_label="Aggregated Distance",
        y_range_name=y_column2_range,
    )
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = "vertical"
    p.add_tools(
        HoverTool(
            tooltips=[
                (aggregated_by[:-1], "@x_axis_formatted"),
                ("Duration", "@duration_formatted h"),
                ("Distance", "@distance km"),
            ]
        )
    )
    p.legend.label_text_font = Style.font
    p.legend.location = "top_left"
    script, div = components(p)

    return script, div, aggregated_by


def _determine_grouping_invterval(time_diff: pd.Timedelta) -> str:
    if time_diff > pd.Timedelta(weeks=20):
        aggregated_by = "Months"
    elif time_diff > pd.Timedelta(weeks=400):
        print("would aggregate by quarter here")
    else:
        aggregated_by = "Weeks"
    log.debug(f"aggregating data for workload plot by: {aggregated_by}")
    return aggregated_by
