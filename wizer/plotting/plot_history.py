import logging
import datetime

import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
import pytz

from django.utils import timezone
from django.conf import settings

log = logging.getLogger(__name__)


def _plot_activities(activities, sport_model, settings_model):
    df = pd.DataFrame(list(activities.values('name', 'sport', 'date', 'duration')))
    sports = sport_model.objects.filter(id__in=df['sport'].unique())
    colors = []
    for sport in sports:
        df[sport.name] = df.loc[df['sport'] == sport.id, 'duration']  # add duration of sports in new column each
        colors.append(sport.color)

    df.drop(columns=['sport', 'duration', 'name'], inplace=True)
    n_days = settings_model.objects.get(pk=1).number_of_days
    today = timezone.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    if n_days < 9999:
        start = today - datetime.timedelta(days=n_days)
    else:
        start = df['date'].min().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    date_range = pd.DataFrame({'date': pd.date_range(start=start, end=today, tz=settings.TIME_ZONE)})
    df = pd.concat([df, date_range], sort=True)

    df['date'] = pd.to_datetime(df['date'], utc=True).dt.date
    df = df.groupby('date', as_index=False).sum()  # group date duplicates to ensure actual stacking of vbars
    df['date_name'] = df['date'].astype(str)
    df.fillna(value=pd.Timedelta(seconds=0), inplace=True)

    p = figure(x_axis_type='datetime', y_axis_type='datetime', plot_height=settings.PLOT_HEIGHT,
               sizing_mode='stretch_width', tools="hover,wheel_zoom,box_zoom,reset,save",
               tooltips="$name @date_name: @$name", )

    sports_list = [sport.name for sport in sports]
    p.vbar_stack(sports_list, x='date', width=datetime.timedelta(days=0.8), color=colors,
                 muted_color=colors, muted_alpha=0.2, source=df,
                 legend_label=sports_list)

    # render zero hours properly
    p.yaxis.major_label_overrides = {0: "0h"}
    p.legend.location = "top_left"
    p.legend.click_policy = "mute"
    p.legend.label_text_font = "ubuntu"

    return p


def plot_history(activities, sport_model, settings_model):
    try:
        script, div = components(_plot_activities(activities=activities, sport_model=sport_model,
                                                  settings_model=settings_model))
    except AttributeError and TypeError and ValueError as e:
        log.warning(f"Could not render plot. Check if activity data is correct: {e}", exc_info=True)
        script = ""
        div = "Could not render plot - no activity data found."
    return script, div
