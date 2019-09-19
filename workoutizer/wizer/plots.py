import logging
import datetime

import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

from django.conf import settings

log = logging.getLogger("wizer.plots")


def plot_activities(activities):
    data = list()
    sports = list()
    dates = list()
    activity_dates = list()
    colors = list()

    for a in activities:
        activity_dates.append(a.date)
        sports.append(a.sport.name)

    oldest = min(activity_dates) - datetime.timedelta(days=1)
    today = datetime.datetime.today().date()

    while oldest <= today:
        dates.append(oldest)
        oldest = oldest + datetime.timedelta(days=1)

    for date in dates:
        durations = list()
        for a in activities:
            if a.date == date:
                durations.append(a.duration)
            else:
                durations.append(0)
        data.append(durations)

    df = pd.DataFrame(data=data, columns=sports, index=dates)
    df = df.groupby(df.columns, axis=1).sum()
    p = figure(x_axis_type='datetime', plot_height=settings.PLOT_HEIGHT, sizing_mode='stretch_width')

    for sport in df.columns:
        for a in activities:
            if str(sport) == str(a.sport):
                colors.append(a.sport.color)
                break

    data = {
        'xs': [df.index.values] * len(df.columns),
        'ys': [df[name].values for name in df],
        'legend': df.columns,
        'colors': colors,
    }

    p.multi_line(xs='xs', ys='ys', color='colors', line_width=4, legend='legend', hover_line_color='colors',
                 hover_line_alpha=1.0, source=ColumnDataSource(data))
    p.xaxis[0].ticker.desired_num_ticks = 12
    p.legend.label_text_font = "Ubuntu"
    p.legend.location = "top_left"

    # TODO: add custom tool tip with sport icon: https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#custom-tooltip
    p.add_tools(HoverTool(
        show_arrow=True,
        line_policy='next',
        tooltips=[
            ('Sport', '@legend'),
            ('Duration', '$y'),
        ],
    ))

    return p


def create_plot(activities):
    try:
        script, div = components(plot_activities(activities=activities))
    except AttributeError and TypeError as e:
        log.error(f"Error rendering plot. Check if activity data is correct: {e}", exc_info=True)
        script = div = "Error rendering Plot"
    return script, div
