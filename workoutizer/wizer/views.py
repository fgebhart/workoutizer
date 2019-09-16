import logging
import datetime
import json

import webcolors
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View

from .models import Sport, Activity, Settings
from .forms import SettingsForm
from .plots import create_plot
from wizer.gis.gis import GeoTrace, bounding_coordinates


log = logging.getLogger('wizer.views')


class DashboardView(View):
    template_name = "dashboard.html"
    sports = Sport.objects.all().order_by('name')
    number_of_days = None
    days_choices = None
    settings = None

    def get_days_config(self, request):
        self.settings = Settings.objects.get(user_id=request.user.id)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = Settings.days_choices

    def get(self, request):
        self.sports = Sport.objects.all().order_by('name')
        self.get_days_config(request)
        today = datetime.datetime.today()
        start_day = today - datetime.timedelta(days=self.number_of_days)
        activities = Activity.objects.filter(date__range=[start_day, today]).order_by("-date")
        script, div = create_plot(activities=activities)
        return render(request, self.template_name,
                      {'sports': self.sports, 'activities': activities, 'script': script, 'div': div,
                       'days': self.number_of_days, 'choices': self.days_choices})


def settings_view(request):
    sports = Sport.objects.all().order_by('name')
    user_id = request.user.id
    settings = Settings.objects.get(user_id=user_id)
    form = SettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            return HttpResponseRedirect('/settings')
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, "settings.html", {'sports': sports, 'form': form, 'settings': settings})


def set_number_of_days(request, number_of_days):
    n = Settings.objects.get(user_id=request.user)
    n.number_of_days = number_of_days
    n.save()
    return redirect(request.META.get('HTTP_REFERER'))


class MapView(View):
    number_of_days = None
    days_choices = None
    settings = None
    corner = None

    def get(self, request, list_of_activities: list):
        log.debug(f"got list_of_activity_ids: {list_of_activities}")
        log.debug(f"user: {request.user.id}")
        self.settings = Settings.objects.get(user_id=request.user.id)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = Settings.days_choices
        traces = []
        all_coordinates = []
        color = '#ffa500'
        for a in list_of_activities:
            if a.trace_file:
                coordinates = json.loads(a.trace_file.coordinates)
                all_coordinates.append(coordinates)
                color = webcolors.name_to_hex(a.sport.color)    # NOTE: last activity color will be applied
                traces.append(GeoTrace(
                    sport=a.sport.name,
                    color=color,
                    center_lat=a.trace_file.center_lat,
                    center_lon=a.trace_file.center_lon,
                    coordinates=coordinates))
                log.debug(f"stored coordinates of: '{a}' in traces list")
        if all_coordinates:
            self.corner = bounding_coordinates(all_coordinates)
        log.debug(f"all coordinates: {all_coordinates}")
        log.debug(f"bounding box corners: {self.corner}")
        return {'traces': traces, 'corner': self.corner, 'settings': self.settings, 'days': self.number_of_days,
                'choices': self.days_choices, 'color': color}
