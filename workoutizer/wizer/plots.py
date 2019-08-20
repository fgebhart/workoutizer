import logging
from datetime import datetime as dt
from datetime import timedelta

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from django.conf import settings

log = logging.getLogger("wizer.plots")


def plot_activities(activities, sports, number_of_days):
    data = list()
    columns = list()
    dates = list()
    colors = list()

    for s in sports:
        columns.append(s.name)
        colors.append(s.color)

    for a in activities:
        durations = list()
        dates.append(a.date)
        for s in sports:
            if a.sport == s:
                durations.append(int(a.duration))
            else:
                durations.append(0)
        data.append(durations)

    log.info(f"data: {data}")
    log.info(f"data: {len(data)}")
    log.info(f"columns: {columns}")
    log.info(f"columns: {len(columns)}")
    log.info(f"dates: {dates}")
    log.info(f"dates: {len(dates)}")

    index = pd.date_range(start=dt.today() - timedelta(days=len(data) - 1), end=dt.today(), freq='d')
    log.debug(f"index: {index}")
    df = pd.DataFrame(data=data, columns=columns, index=dates)

    p = figure(
        x_axis_type='datetime',
        plot_width=settings.PLOT_WIDTH,
        plot_height=settings.PLOT_HEIGHT,
    )

    data = {
        'xs': [df.index.values] * len(df.columns),
        'ys': [df[name].values for name in df],
        'legend': columns,
        'colors': colors,
    }
    source = ColumnDataSource(data)

    p.multi_line(xs='xs', ys='ys', color='colors',
                 line_width=3, legend='legend', source=source)
    p.legend.location = "top_left"

    return p
