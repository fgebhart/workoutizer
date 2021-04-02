import logging
import datetime

import pandas as pd
from bokeh.plotting import figure
from bokeh.models import BoxZoomTool
from bokeh.embed import components
import pytz

from django.utils import timezone
from django.conf import settings

log = logging.getLogger(__name__)


def _plot_activities(activities, sport_model, number_of_days):
    df = pd.DataFrame(list(activities.values("name", "sport", "date", "duration")))
    sports = sport_model.objects.filter(id__in=df["sport"].unique())
    colors = []
    for sport in sports:
        df[sport.name] = df.loc[df["sport"] == sport.id, "duration"]  # add duration of sports in new column each
        colors.append(sport.color)

    df.drop(columns=["sport", "duration", "name"], inplace=True)
    today = timezone.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    if number_of_days < 9999:
        start = today - datetime.timedelta(days=number_of_days)
    else:
        start = df["date"].min().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    date_range = pd.DataFrame({"date": pd.date_range(start=start, end=today, tz=settings.TIME_ZONE)})
    df = pd.concat([df, date_range], sort=True)

    df["date"] = pd.to_datetime(df["date"], utc=True).dt.date
    df = df.groupby("date", as_index=False).sum()  # group date duplicates to ensure actual stacking of vbars
    df["date_name"] = df["date"].astype(str)
    df.fillna(value=pd.Timedelta(seconds=0), inplace=True)

    p = figure(
        x_axis_type="datetime",
        y_axis_type="datetime",
        plot_height=settings.PLOT_HEIGHT,
        sizing_mode="stretch_width",
        tools="hover,reset",
        tooltips="$name @date_name",
        # tooltips="$name @date_name: @$name",
    )

    sports_list = [sport.name for sport in sports]
    p.vbar_stack(
        sports_list,
        x="date",
        width=datetime.timedelta(days=0.8),
        color=colors,
        muted_color=colors,
        muted_alpha=0.2,
        source=df,
    )

    # render zero hours properly
    p.yaxis.major_label_overrides = {0: "0h"}
    p.toolbar.logo = None

    p.add_tools(BoxZoomTool(dimensions="width"))

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
