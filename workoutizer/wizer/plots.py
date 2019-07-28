import logging
from datetime import datetime, timedelta

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.palettes import brewer

from django.conf import settings

log = logging.getLogger("wizer.plots")


def plot_activities(activities, number_of_days):
    today = datetime.now()
    x_axis_date_range = today - timedelta(days=number_of_days)
    pd = PlotData()

    for a in activities:
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

    log.debug(f"pd.date: {pd.date}")
    log.debug(f"pd.sports: {pd.sports}")
    log.debug(f"pd.duration: {pd.data}")
    colors = pd.get_uniques('sport_color')
    log.debug(f"pd.sport_color: {colors}")

    log.debug(f"pd.get_dict(): {pd.get_dict()}")
    source = ColumnDataSource(data=pd.get_dict())

    p = figure(
        x_axis_type='datetime',
        x_range=(x_axis_date_range, today),
        plot_width=settings.PLOT_WIDTH,
        plot_height=settings.PLOT_HEIGHT,
    )
    p.varea_stack(pd.get_uniques("sports"), x='date_axis', source=source, fill_color=colors)

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

    def get_uniques(self, attribute):
        return list(dict.fromkeys(getattr(self, attribute)))
