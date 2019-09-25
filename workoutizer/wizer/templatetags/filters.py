import logging

from django import template


log = logging.getLogger('wizer.filters')

register = template.Library()


@register.filter
def duration(td):
    log.debug(f"filtering duration: {td}")
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return '{}h {}m'.format(hours, minutes)
