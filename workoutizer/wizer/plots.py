from dataclasses import dataclass
import numpy as np
import logging
from datetime import datetime, timedelta

from bokeh.models import ColumnDataSource
from bokeh.core.properties import value
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import brewer


import pandas as pd

log = logging.getLogger("wizer.plots")


def plot_activities(activities, number_of_days):
    today = datetime.now()
    x_axis_date_range = today - timedelta(days=number_of_days)
    pd = PlotData()

    for a in activities:
        # log.debug(f"my list pd.date: {pd.date}")
        # log.debug(f"a.date: {a.date}")
        pd.date.append(a.date)
        pd.sports.append(str(a.sport))
        pd.sport_color.append(str(a.sport.color))
    for sport in pd.sports:
        pd.data[sport] = []
        for a in activities:
            if str(a.sport) == sport:
                pd.data[sport].append(int(a.duration))
            else:
                pd.data[sport].append(0)

    bkdict = dict(x=pd.date[:5], y1=[1, 2, 4, 3, 4], y2=[1, 4, 2, 2, 3])

    log.debug(f"pd.date: {pd.date}")
    log.debug(f"pd.sports: {pd.sports}")
    log.debug(f"pd.duration: {pd.data}")
    log.debug(f"bkdict: {bkdict}")

    log.debug(f"pd.get_dict(): {pd.get_dict()}")
    source = ColumnDataSource(data=pd.get_dict())

    # p = figure(
    #     x_axis_type='datetime',
    #     y_axis_label="Duration",
    #     plot_height=300,
    #     plot_width=1200,
    #     x_range=(end_date, start_date),
    #     # line_color='white', fill_color=factor_cmap('fruits', palette=colors, factors=all_dates)
    # )
    # p.toolbar.logo = None
    # p.toolbar_location = None
    # p.vbar(x=all_dates, top=all_durations, width=0.9, color="#CAB2D6")
    p = figure(x_axis_type='datetime', x_range=(x_axis_date_range, today), plot_width=1200, plot_height=300)
    p.varea_stack(pd.get_sports(), x='date_axis', source=source)

    return p


class PlotData:
    def __init__(self):
        self.date = list()
        self.sports = list()
        self.sport_color = list()
        self.data = dict()

    def get_dict(self):
        self.data['date_axis'] = self.date
        return self.data

    def get_sports(self):
        return list(dict.fromkeys(self.sports))
