import logging
import datetime
import json

import webcolors
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages

from .models import Sport, Activity, Settings
from .forms import SettingsForm
from .plots import create_plot
from wizer.gis.gis import GeoTrace

log = logging.getLogger('wizer.views')


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
        for a in list_of_activities:
            if a.trace_file:
                coordinates = json.loads(a.trace_file.coordinates)
                color = webcolors.name_to_hex(a.sport.color)  # NOTE: last activity color will be applied
                if coordinates:
                    traces.append(GeoTrace(
                        sport=a.sport.name,
                        color=color,
                        coordinates=coordinates))
                    log.debug(f"stored coordinates of: '{a}' in traces list")
        return {'traces': traces, 'settings': self.settings, 'days': self.number_of_days,
                'choices': self.days_choices, 'color': color}


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
            activities = Activity.objects.filter(date__range=[start_day, today], sport=sport_id).exclude(
                sport_id=None).order_by("-date")
        else:
            activities = Activity.objects.filter(date__range=[start_day, today]).exclude(sport_id=None).order_by(
                "-date")
        return activities

    def create_plot(self, activities):
        pass


class DashboardView(View, PlotView):
    template_name = "dashboard.html"
    sports = Sport.objects.all().order_by('name')

    def get(self, request):
        self.sports = Sport.objects.all().order_by('name')
        activities = self.get_activities()
        summary = get_summary_of_activities(activities=activities)
        script, div = create_plot(activities=activities, plotting_style=self.settings.plotting_style)
        return render(request, self.template_name,
                      {'sports': self.sports, 'activities': activities, 'script': script, 'div': div,
                       'days': self.number_of_days, 'choices': self.days_choices, 'summary': summary})


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
    return {'count': len(activities), 'duration': int(sum([n.duration for n in activities]) / 60),
            'distance': int(sum([n.distance for n in activities]))}
