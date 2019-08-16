import logging
import datetime
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from django.conf import settings


log = logging.getLogger("wizer.plots")


def plot_activities(activities, sports, number_of_days):
    today = datetime.datetime.now()
    x_axis_date_range = list()
    for i in range(number_of_days):
        x_axis_date_range.append(today - datetime.timedelta(days=i))
    log.debug(f"created x axis datetime list: {x_axis_date_range}")
    log.debug(f"len x axis datetime list: {len(x_axis_date_range)}")

    data = {
        'activity_data': list(),
        'time_x_axis': list(),
        'colors': [c.color for c in sports],
        'sports': [s.name for s in sports],
    }

    for sport in data['sports']:
        durations = list()
        for a in activities:
            if str(a.sport) == sport:
                durations.append(int(a.duration))
            else:
                durations.append(0)
        data['activity_data'].append(durations)

    for i in range(len(data['sports'])):
        data['time_x_axis'].append(x_axis_date_range)

    log.debug(f"data: {data}")
    source = ColumnDataSource(data=data)

    p = figure(
        x_axis_type='datetime',
        plot_width=settings.PLOT_WIDTH,
        plot_height=settings.PLOT_HEIGHT,
    )
    p.multi_line(xs='time_x_axis', ys='activity_data', legend='sports', color='colors', source=source, line_width=3)
    p.legend.location = "top_left"

    return p


class PlotData:
    def __init__(self):
        self.date = list()
        self.sports = list()
        self.sport_color = list()
        self.data = list()

    def get_data(self):
        return self.data

    def get_uniques(self, attribute):
        return list(dict.fromkeys(getattr(self, attribute)))
