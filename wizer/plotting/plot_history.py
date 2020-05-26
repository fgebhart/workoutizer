import logging

import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

from django.conf import settings
from wizer.models import Sport

log = logging.getLogger(__name__)


def _plot_activities(activities, plotting_style="line"):
    sports = Sport.objects.all().exclude(name='unknown')
    df = pd.DataFrame(list(activities.values('name', 'sport', 'date', 'duration')))
    colors = []
    for sport in sports:
        df[sport.name] = df.loc[df['sport'] == sport.id, 'duration']
        colors.append(sport.color)

    df.drop(columns=['sport', 'duration', 'name'], inplace=True)
    df.fillna(value=pd.Timedelta(seconds=0), inplace=True)

    p = figure(x_axis_type='datetime', y_axis_type='datetime', plot_height=settings.PLOT_HEIGHT,
               sizing_mode='stretch_width', toolbar_location=None, tools="hover", tooltips="$name @date: @$name")

    sports_list = [sport.name for sport in sports]
    p.vbar_stack(sports_list, x='date', width=70000000, color=colors, source=df,
                 legend_label=sports_list)

    return p


def plot_history(activities, plotting_style):
    try:
        script, div = components(_plot_activities(activities=activities, plotting_style=plotting_style))
    except AttributeError and TypeError and ValueError as e:
        log.warning(f"Could not render plot. Check if activity data is correct: {e}", exc_info=True)
        script = ""
        div = "Could not render plot - no activity data found."
    return script, div
