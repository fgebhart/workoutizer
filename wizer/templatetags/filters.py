import datetime

from django import template
from django.db.models.query import QuerySet


register = template.Library()


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f'{hours}h {minutes}m'


@register.filter
def table_duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if minutes < 10:
        minutes = f"0{minutes}"
    return f'{hours}:{minutes}'


@register.filter
def speed_to_pace(speed):
    if speed is None:
        return "00:00"
    if speed <= 0:
        return "00:00"
    pace = (float(speed) * 60 / 1000) ** -1
    delta = datetime.timedelta(minutes=pace)
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    pace = '{:02}:{:02}'.format(int(minutes), int(seconds))
    return f'{pace}'


@register.filter
def m_per_s_to_km_per_h(m_per_s):
    return round(float(m_per_s) * 3.6, 1)


@register.filter
def round_2nd_decimal(td):
    return round(td, 2)


@register.filter
def to_int(number):
    return int(number)


@register.filter
def h_m_s(delta):
    return str(delta).split(".")[0]


def strfdelta(tdelta, format):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return format.format(**d)


@register.filter
def queryset_to_list(queryset):
    if isinstance(queryset, QuerySet):
        list_as_string = sorted(list(queryset.values_list('slug', flat=True)))
        if 'unknown' in list_as_string:
            list_as_string.remove('unknown')
        return list_as_string
