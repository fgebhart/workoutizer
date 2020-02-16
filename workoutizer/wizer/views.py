import logging
import datetime
import json

import webcolors
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages

from wizer.models import Sport, Activity, Settings
from wizer.forms import SettingsForm
from wizer.plots import create_plot, plot_pie_chart
from wizer.gis.gis import GeoTrace, add_elevation_data_to_coordinates

log = logging.getLogger(__name__)


class MapView(View):
    number_of_days = None
    days_choices = None
    settings = None

    def get(self, request, list_of_activities: list):
        log.debug(f"got list_of_activity_ids: {list_of_activities}")
        self.settings = Settings.objects.get(pk=1)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = Settings.days_choices
        traces = []
        color = '#ffa500'
        sport = None
        has_elevation = False
        for activity in list_of_activities:
            if activity.trace_file:
                coordinates = json.loads(activity.trace_file.coordinates)
                if activity.trace_file.elevation:
                    has_elevation = True
                    elevation = json.loads(activity.trace_file.elevation)
                    coordinates = add_elevation_data_to_coordinates(coordinates, elevation)
                try:
                    color = webcolors.name_to_hex(activity.sport.color)  # NOTE: last activity color will be applied
                    sport = activity.sport.name
                except AttributeError as e:
                    log.warning(f"could not find color of sport: {sport}, using default color instead: {e}")
                if coordinates:
                    traces.append(GeoTrace(
                        pk=activity.pk,
                        name=activity.name,
                        sport=sport,
                        color=color,
                        coordinates=coordinates))
                    log.debug(f"stored coordinates of: '{activity}' in traces list")
        return {'traces': traces, 'settings': self.settings, 'days': self.number_of_days,
                'choices': self.days_choices, 'color': color, 'has_elevation': has_elevation}


class PlotView:
    number_of_days = None
    days_choices = None
    settings = None

    def get_days_config(self):
        self.settings = Settings.objects.get(pk=1)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = Settings.days_choices

    def get_activities(self, sport_id=None):
        self.get_days_config()
        today = datetime.datetime.today()
        start_day = today - datetime.timedelta(days=self.number_of_days)
        if sport_id:
            activities = Activity.objects.filter(date__range=[start_day, today], sport=sport_id).order_by("-date")
        else:
            activities = Activity.objects.filter(date__range=[start_day, today]).order_by("-date")
        return activities


class DashboardView(View, PlotView):
    template_name = "dashboard.html"
    sports = Sport.objects.all().order_by('name')

    def get(self, request):
        self.sports = Sport.objects.all().order_by('name')
        activities = self.get_activities()
        summary = get_summary_of_activities(activities=activities)
        script, div = create_plot(activities=activities, plotting_style=self.settings.plotting_style)
        script_pc, div_pc = plot_pie_chart(activities=activities)
        return render(request, self.template_name,
                      {'sports': self.sports, 'activities': activities, 'script': script, 'div': div,
                       'days': self.number_of_days, 'choices': self.days_choices, 'summary': summary,
                       'script_pc': script_pc, 'div_pc': div_pc})


def settings_view(request):
    sports = Sport.objects.all().order_by('name')
    settings = Settings.objects.get(pk=1)
    form = SettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, 'Successfully saved Settings!')
            return HttpResponseRedirect('/settings')
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, "settings.html", {'sports': sports, 'form': form, 'settings': settings})


def set_number_of_days(request, number_of_days):
    n = Settings.objects.get(pk=1)
    n.number_of_days = number_of_days
    log.debug(f"number of days: {number_of_days}")
    n.save()
    return redirect(request.META.get('HTTP_REFERER'))


def get_summary_of_activities(activities):
    total_duration = datetime.timedelta(minutes=0)
    for a in activities:
        total_duration += a.duration
    log.debug(f"total duration of selected activities: {total_duration}")
    return {'count': len(activities), 'duration': total_duration,
            'distance': int(sum([n.distance for n in activities]))}


def custom_404_view(request, exception=None):
    response = render_to_response("lib/404.html")
    response.status_code = 404
    return response
