import pandas as pd
from bokeh.embed import components
from bokeh.models import HoverTool, LinearAxis, Range1d
from bokeh.plotting import figure
from bokeh.transform import dodge

from wkz import models
from wkz.tools.style import Style

BAR_WIDTH = 0.35
BAR_DODGE = 0.125


def plot_workload(activity_model: models.Activity):
    df = pd.DataFrame(list(activity_model.objects.all().values("distance", "duration", "date")))

    duration_df = df[["date", "duration"]]
    distance_df = df[["date", "distance"]]

    # TODO: check if first date is >= 3 months away, if yes groupby by months, if not groupby weeks

    # groupby week
    aggregated_by = "Weeks"
    df = duration_df.groupby(pd.Grouper(freq="W", key="date")).sum().reset_index().sort_values("date")
    df["distance"] = (
        distance_df.groupby(pd.Grouper(freq="W", key="date")).sum().reset_index().sort_values("date")["distance"]
    )
    del distance_df
    del duration_df
    g = df.groupby(pd.Grouper(freq="W", key="date"))["date"]
    df["week_begin"] = g.transform("first").dt.date
    df["week_end"] = df["week_begin"] + pd.Timedelta(days=7)
    df["week"] = g.transform("first").dt.strftime("%-m/%d")
    df["week_formatted"] = df["week_begin"].astype(str) + " - " + df["week_end"].astype(str)
    df.drop(columns="date", inplace=True)
    df["duration_formatted"] = df["duration"].dt.to_pytimedelta().astype(str)

    p = figure(
        height=200,
        x_range=df["week"].to_list(),
        toolbar_location=None,
        sizing_mode="stretch_width",
        y_axis_type="datetime",
    )
    p.tools = []
    p.y_range.start = 0

    p.vbar(
        x=dodge("week", -BAR_DODGE, range=p.x_range),
        top="duration",
        width=BAR_WIDTH,
        source=df,
        fill_color="#FCC468",
        line_color="white",
        legend_label="Aggregated Duration",
    )
    p.yaxis.major_label_overrides = {0: "0h"}
    p.yaxis.major_label_text_font = Style.font
    p.xaxis.major_label_text_font = Style.font
    p.yaxis.axis_label = "Duration"
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
        x=dodge("week", BAR_DODGE, range=p.x_range),
        top="distance",
        width=BAR_WIDTH,
        source=df,
        fill_color="#F17E5D",
        line_color="white",
        legend_label="Aggregated Distance",
        y_range_name=y_column2_range,
    )
    p.xgrid.grid_line_color = None
    p.add_tools(
        HoverTool(
            tooltips=[("Week", "@week_formatted"), ("Duration", "@duration_formatted h"), ("Distance", "@distance km")]
        )
    )
    p.legend.label_text_font = Style.font
    script, div = components(p)

    return script, div, aggregated_by
