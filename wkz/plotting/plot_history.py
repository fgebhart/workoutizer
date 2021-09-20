import datetime
import logging

import pandas as pd
import pytz
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.plotting import figure
from django.utils import timezone

from wkz.tools.style import font
from workoutizer import settings as django_settings

log = logging.getLogger(__name__)


def _plot_activities(activities, sport_model, number_of_days):
    df = pd.DataFrame(list(activities.values("name", "sport", "date", "duration")))
    sports = sport_model.objects.filter(id__in=df["sport"].unique())
    colors = []
    for sport in sports:
        df[sport.name] = df.loc[df["sport"] == sport.id, "duration"]  # add duration of sports in new column each
        colors.append(sport.color)

    df.drop(columns=["sport", "duration", "name"], inplace=True)
    today = timezone.now().replace(tzinfo=pytz.timezone(django_settings.TIME_ZONE))
    if number_of_days < 9999:
        start = today - datetime.timedelta(days=number_of_days)
    else:
        start = df["date"].min().replace(tzinfo=pytz.timezone(django_settings.TIME_ZONE))
    date_range = pd.DataFrame({"date": pd.date_range(start=start, end=today, tz=django_settings.TIME_ZONE)})
    df = pd.concat([df, date_range], sort=True)

    df["date"] = pd.to_datetime(df["date"], utc=True).dt.date
    df = df.groupby("date", as_index=False).sum()  # group date duplicates to ensure actual stacking of vbars
    df["date_formatted"] = df["date"].astype(str)
    df.fillna(value=pd.Timedelta(seconds=0), inplace=True)
    for sport in sports:
        # add formatted duration
        df[f"{sport.name}_duration"] = df[sport.name].dt.to_pytimedelta().astype(str)

    p = figure(
        x_axis_type="datetime",
        y_axis_type="datetime",
        plot_height=django_settings.PLOT_HEIGHT,
        sizing_mode="stretch_width",
    )
    p.tools = []

    sports_list = [sport.name for sport in sports]
    renderers = p.vbar_stack(
        sports_list,
        x="date",
        width=datetime.timedelta(days=0.8),
        color=colors,
        source=df,
    )
    for r in renderers:
        sport = r.name
        hover = HoverTool(
            tooltips=[("%s" % sport, "@%s" % f"{sport}_duration h"), ("Date", "@date_formatted")], renderers=[r]
        )
        p.add_tools(hover)

    # render zero hours properly
    p.yaxis.major_label_overrides = {0: "0h"}
    p.yaxis.major_label_text_font = font
    p.xaxis.major_label_text_font = font
    p.toolbar.logo = None
    p.toolbar_location = None

    return p


def plot_history(activities, sport_model, number_of_days):
    try:
        script, div = components(
            _plot_activities(activities=activities, sport_model=sport_model, number_of_days=number_of_days)
        )
    except AttributeError and TypeError and ValueError as e:
        log.warning(f"Could not render plot. Check if activity data is correct: {e}", exc_info=True)
        script = ""
        div = "Could not render plot - no activity data found."
    return script, div
