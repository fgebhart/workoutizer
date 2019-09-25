import logging

from django import template


log = logging.getLogger('wizer.filters')

register = template.Library()


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return '{}h {}m'.format(hours, minutes)


@register.filter
def table_duration(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if minutes < 10:
        minutes = f"0{minutes}"
    return '{}:{}'.format(hours, minutes)
