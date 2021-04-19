import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure

from wkz import models


def plot_trend(activities, sport_model):
    number_of_days = models.get_settings().number_of_days

    df = pd.DataFrame.from_records(activities.values("sport_id", "duration", "date"))
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    days = int(number_of_days / 5)
    freq = days if days > 1 else 1
    df = df.groupby([pd.Grouper(freq=f"{freq}D"), "sport_id"]).agg({"duration": np.sum}).reset_index()
    df = df.pivot(index="date", columns="sport_id", values="duration").fillna("0")
    sports = sport_model.objects.exclude(name="unknown").order_by("id").values("id", "name", "color")
    id_color_mapping = {}
    for sport in sports:
        id_color_mapping[sport["id"]] = sport["color"]
    df = df.rename(columns=id_color_mapping)

    p = figure(
        height=135,
        sizing_mode="stretch_width",
        x_axis_type="datetime",
        y_axis_type="datetime",
    )
    p.multi_line(
        xs=[df.index.values] * len(df.columns), ys=[df[name].values for name in df], line_color=df.columns, line_width=3
    )

    # render zero hours properly
    p.yaxis.major_label_overrides = {0: "0h"}
    p.toolbar.logo = None
    p.toolbar_location = None
    p.tools = []

    script_trend, div_trend = components(p)

    return script_trend, div_trend
