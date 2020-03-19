import logging

import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

log = logging.getLogger(__name__)


def plot_time_series(trace_data):

    df = pd.DataFrame(data=data, columns=sports, index=dates, dtype='timedelta64[ns]')
    df = df.groupby(df.columns, axis=1).sum()

    p = figure(x_axis_type='datetime', y_axis_type='datetime', plot_height=settings.PLOT_HEIGHT,
               sizing_mode='stretch_width',
               tools="pan,wheel_zoom,box_zoom,reset,save")


    p.vbar_stack(sports, x='dates', width=70000000, color=colors, source=plot_data)

    p.xaxis[0].ticker.desired_num_ticks = 12
    p.toolbar.logo = None
    p.toolbar_location = None

    script, div = components(p)

    return script, div
