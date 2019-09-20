import logging
import datetime

import pandas as pd
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.embed import components

from django.conf import settings

log = logging.getLogger("wizer.plots")


def plot_activities(activities, plotting_style="line"):
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

    for sport in df.columns:
        for a in activities:
            if str(sport) == str(a.sport):
                colors.append(a.sport.color)
                break

    p = figure(x_axis_type='datetime', plot_height=settings.PLOT_HEIGHT, sizing_mode='stretch_width',
               tools="pan,wheel_zoom,box_zoom,reset,save")

    if plotting_style == "line":
        data = {
            'xs': [df.index.values] * len(df.columns),
            'ys': [df[name].values for name in df],
            'legend': df.columns,
            'colors': colors,
        }

        p.multi_line(xs='xs', ys='ys', color='colors', line_width=4, legend='legend', hover_line_color='colors',
                     hover_line_alpha=1.0, source=ColumnDataSource(data))

        p.add_tools(HoverTool(
            show_arrow=True,
            line_policy='next',
            tooltips=[
                ('Sport', '@legend'),
                ('Duration', '$y'),
            ],))
    else:
        sports = df.columns

        plot_data = {}
        for d, s in zip([df[name].values for name in df], sports):
            plot_data[s] = d
        plot_data['dates'] = dates

        p.vbar_stack(sports, x='dates', width=70000000, color=colors, source=plot_data,
                     legend=[value(x) for x in sports])
        p.add_tools(HoverTool(tooltips="$name: @$name min",))

    p.legend.label_text_font = "Ubuntu"
    p.legend.location = "top_left"
    p.xaxis[0].ticker.desired_num_ticks = 12

    return p


def create_plot(activities, plotting_style):
    try:
        script, div = components(plot_activities(activities=activities, plotting_style=plotting_style))
    except AttributeError and TypeError as e:
        log.error(f"Error rendering plot. Check if activity data is correct: {e}", exc_info=True)
        script = div = "Error rendering Plot"
    return script, div
