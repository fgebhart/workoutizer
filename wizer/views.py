import logging
import datetime
import json

import pandas as pd

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages
from multiprocessing import Process
from django.urls import reverse
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from wizer import models
from wizer import forms
from wizer.plotting.plot_history import plot_history
from wizer.plotting.plot_pie_chart import plot_pie_chart
from wizer.plotting.plot_trend import plot_trend
from wizer.gis.gis import GeoTrace
from wizer.file_helper.reimporter import Reimporter
from wizer.file_helper.fit_collector import try_to_mount_device, FitCollector
from wizer.tools.colors import lines_colors
from wizer.tools.utils import cut_list_to_have_same_length, limit_string
from workoutizer import settings

log = logging.getLogger(__name__)


def get_all_form_field_ids():
    """
    helper function to get all ids of input form fields to avoid keyboard navigation while entering
    text into form fields.
    """

    ids = []
    all_forms = [forms.AddSportsForm, forms.EditSettingsForm, forms.AddActivityForm, forms.EditActivityForm]
    for form in all_forms:
        ids += [f"id_{field}" for field in form.base_fields.keys()]
    return ids


class WKZView(View):
    sports = models.Sport.objects.all().order_by('name')
    form_field_ids = get_all_form_field_ids()
    context = {"sports": sports, "form_field_ids": form_field_ids}


class MapView(View):
    number_of_days = None
    days_choices = None
    settings = None

    def get(self, request, list_of_activities: list):
        log.debug(f"got list_of_activity_ids: {list_of_activities}")
        self.settings = models.Settings.objects.get(pk=1)
        setattr(self.settings, "trace_width", settings.trace_line_width)
        setattr(self.settings, "trace_opacity", settings.trace_line_opacity)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = models.Settings.days_choices
        traces = []
        for activity in list_of_activities:
            if activity.trace_file:
                coordinates = json.dumps(list(zip(
                    list(pd.Series(json.loads(activity.trace_file.longitude_list)).ffill().bfill()),
                    list(pd.Series(json.loads(activity.trace_file.latitude_list)).ffill().bfill()),
                )))
                sport = activity.sport.name
                if coordinates:
                    traces.append(GeoTrace(
                        pk=activity.pk,
                        name=activity.name,
                        sport=sport,
                        coordinates=coordinates))
        has_traces = True if traces else False

        if traces:
            traces, colors = cut_list_to_have_same_length(traces, lines_colors, mode='fill end',
                                                          modify_only_list2=True)
            traces = zip(traces, colors)
        return {'traces': traces, 'settings': self.settings, 'days': self.number_of_days,
                'choices': self.days_choices, 'has_traces': has_traces}


class PlotView:
    number_of_days = None
    days_choices = None
    settings = None

    def get_days_config(self):
        self.settings = models.Settings.objects.get_or_create(pk=1)[0]
        self.number_of_days = self.settings.number_of_days
        self.days_choices = models.Settings.days_choices

    def get_activities(self, sport_id=None):
        self.get_days_config()
        now = timezone.now()
        start_datetime = now - datetime.timedelta(days=self.number_of_days)
        if sport_id:
            activities = models.Activity.objects.filter(date__range=[start_datetime, now], sport=sport_id).order_by(
                "-date")
        else:
            activities = models.Activity.objects.filter(date__range=[start_datetime, now]).order_by("-date")
        return activities


class DashboardView(View, PlotView):
    template_name = "dashboard.html"
    sports = models.Sport.objects.all().order_by('name')

    def get(self, request):
        self.sports = models.Sport.objects.all().order_by('name')
        activities = self.get_activities()
        summary = get_summary_of_activities(activities=activities)
        context = {
            'sports': self.sports,
            'activities': activities,
            'days': self.number_of_days,
            'choices': self.days_choices,
            'summary': summary,
            'page': 'dashboard',
            'form_field_ids': get_all_form_field_ids(),
        }
        if activities:
            script_history, div_history = plot_history(activities=activities, sport_model=models.Sport,
                                                       settings_model=models.Settings)
            script_pc, div_pc = plot_pie_chart(activities=activities)
            script_trend, div_trend = plot_trend(activities=activities, sport_model=models.Sport)
            plotting_context = {
                'script_history': script_history,
                'div_history': div_history,
                'script_pc': script_pc,
                'div_pc': div_pc,
                'script_trend': script_trend,
                'div_trend': div_trend,
            }
            return render(request, self.template_name, {**context, **plotting_context})
        else:
            log.warning(f"no activities found...")
        return render(request, self.template_name, {**context})


def settings_view(request):
    sports = models.Sport.objects.all().order_by('name')
    settings = models.Settings.objects.get_or_create(pk=1)[0]
    activities = models.Activity.objects.filter(is_demo_activity=True).count()
    form = forms.EditSettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            log.debug(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, 'Successfully saved Settings!')
            return HttpResponseRedirect(reverse('settings'))
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, "lib/settings.html", {'sports': sports, 'form': form, 'settings': settings,
                                                 'form_field_ids': get_all_form_field_ids(),
                                                 'delete_demos': True if activities else False})


class HelpView(WKZView):
    template_name = "lib/help.html"

    def get(self, request):
        return render(request, template_name=self.template_name, context=self.context)


@api_view(['POST'])
def mount_device_endpoint(request):
    mount_path = try_to_mount_device()
    settings = models.Settings.objects.get_or_create(pk=1)[0]
    if mount_path:
        fit_collector = FitCollector(
            path_to_garmin_device=settings.path_to_garmin_device,
            target_location=settings.path_to_trace_dir,
            delete_files_after_import=settings.delete_files_after_import
        )
        fit_collector.copy_fit_files()
        return Response("mounted", status=status.HTTP_200_OK)
    else:
        return Response("failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def set_number_of_days(request, number_of_days):
    settings = models.Settings.objects.get(pk=1)
    settings.number_of_days = number_of_days
    log.debug(f"number of days: {number_of_days}")
    settings.save()
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('home'))


def get_summary_of_activities(activities):
    total_duration = datetime.timedelta(minutes=0)
    for a in activities:
        total_duration += a.duration
    log.debug(f"total duration of selected activities: {total_duration}")
    return {'count': len(activities), 'duration': total_duration,
            'distance': int(sum([n.distance for n in activities]))}


def custom_404_view(request, exception=None):
    return render(None, "lib/404.html", status=404)


def reimport_activity_files(request):
    messages.info(request, f'Running reimport in background...')

    reimporter = Process(target=Reimporter, args=())
    reimporter.start()

    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(reverse('settings'))
