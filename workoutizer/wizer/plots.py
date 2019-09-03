import logging
import datetime

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

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

    oldest = min(activity_dates)
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
    p = figure(x_axis_type='datetime', plot_width=settings.PLOT_WIDTH, plot_height=settings.PLOT_HEIGHT)

    for sport in df.columns:
        for a in activities:
            log.debug(f"sport {sport}, a.sport {a.sport}")
            if str(sport) == str(a.sport):
                colors.append(a.sport.color)
                break

    data = {
        'xs': [df.index.values] * len(df.columns),
        'ys': [df[name].values for name in df],
        'legend': df.columns,
        'colors': colors,
    }

    p.multi_line(xs='xs', ys='ys', color='colors', line_width=3, legend='legend', source=ColumnDataSource(data))
    # p.legend.label_text_font = "Ubuntu"
    p.legend.location = "top_left"

    return p
