import logging
import json
from typing import List, Union
import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages
from multiprocessing import Process
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum

from wizer import models
from wizer import forms
from wizer.file_importer import reimport_activity_files
from wizer.plotting.plot_history import plot_history
from wizer.plotting.plot_pie_chart import plot_pie_chart
from wizer.plotting.plot_trend import plot_trend
from wizer.gis.geo import GeoTrace, get_list_of_coordinates
from wizer.tools.colors import lines_colors
from wizer.tools.utils import cut_list_to_have_same_length
from workoutizer import settings as django_settings
from wizer import configuration
from workoutizer import __version__


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
    sports = models.Sport.objects.all().order_by("name")
    form_field_ids = get_all_form_field_ids()
    context = {"sports": sports, "form_field_ids": form_field_ids}


class MapView(View):
    number_of_days = None
    days_choices = None
    settings = None

    def get(self, request, list_of_activities: list):
        self.settings = models.get_settings()
        setattr(self.settings, "trace_width", django_settings.trace_line_width)
        setattr(self.settings, "trace_opacity", django_settings.trace_line_opacity)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = models.Settings.days_choices
        traces = []
        for activity in list_of_activities:
            if activity.trace_file:
                coordinates = json.dumps(
                    get_list_of_coordinates(
                        json.loads(activity.trace_file.longitude_list), json.loads(activity.trace_file.latitude_list)
                    )
                )
                sport = activity.sport.name
                if coordinates != "[]":
                    traces.append(GeoTrace(pk=activity.pk, name=activity.name, sport=sport, coordinates=coordinates))
        has_traces = True if traces else False

        if traces:
            traces, colors = cut_list_to_have_same_length(traces, lines_colors, mode="fill end", modify_only_list2=True)
            traces = zip(traces, colors)
        return {
            "traces": traces,
            "settings": self.settings,
            "days": self.number_of_days,
            "choices": self.days_choices,
            "has_traces": has_traces,
        }


class PlotView:
    number_of_days = None
    days_choices = None
    settings = None

    def get_days_config(self):
        self.settings = models.get_settings()
        self.number_of_days = self.settings.number_of_days
        self.days_choices = models.Settings.days_choices

    def get_activity_data_for_plots(self, sport_id=None):
        self.get_days_config()
        now = timezone.now()
        start_datetime = now - datetime.timedelta(days=self.number_of_days)
        if sport_id:
            activities = models.Activity.objects.filter(date__range=[start_datetime, now], sport=sport_id).order_by(
                "-date"
            )
        else:
            activities = models.Activity.objects.filter(date__range=[start_datetime, now]).order_by("-date")
        return activities


class DashboardView(View, PlotView):
    template_name = "dashboard.html"
    sports = models.Sport.objects.all().order_by("name")

    def get(self, request):
        page = 0
        settings = models.get_settings()
        self.sports = models.Sport.objects.all().order_by("name")
        activities = self.get_activity_data_for_plots()
        summary = get_summary_of_all_activities()
        context = {
            "sports": self.sports,
            "current_page": page,
            "is_last_page": False,
            "days": self.number_of_days,
            "choices": self.days_choices,
            "summary": summary,
            "page": "dashboard",
            "form_field_ids": get_all_form_field_ids(),
        }
        if activities:
            script_history, div_history = plot_history(
                activities=activities, sport_model=models.Sport, number_of_days=settings.number_of_days
            )
            script_pc, div_pc = plot_pie_chart(activities=activities)
            script_trend, div_trend = plot_trend(activities=activities, sport_model=models.Sport)
            plotting_context = {
                "script_history": script_history,
                "div_history": div_history,
                "script_pc": script_pc,
                "div_pc": div_pc,
                "script_trend": script_trend,
                "div_trend": div_trend,
                "activities_selected_for_plot": True,
            }
            return render(request, self.template_name, {**context, **plotting_context})
        else:
            log.warning("no activities found...")
            context["activities_selected_for_plot"] = False
        return render(request, self.template_name, {**context})


def settings_view(request):
    sports = models.Sport.objects.all().order_by("name")
    settings = models.get_settings()
    activities = models.Activity.objects.filter(is_demo_activity=True).count()
    form = forms.EditSettingsForm(request.POST or None, instance=settings)
    if request.method == "POST":
        if form.is_valid():
            log.debug(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, "Successfully saved Settings!")
            return HttpResponseRedirect(reverse("settings"))
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(
        request,
        "lib/settings.html",
        {
            "sports": sports,
            "form": form,
            "settings": settings,
            "form_field_ids": get_all_form_field_ids(),
            "delete_demos": True if activities else False,
        },
    )


class HelpView(WKZView):
    template_name = "lib/help.html"

    def get(self, request):
        self.context["version"] = __version__
        return render(request, template_name=self.template_name, context=self.context)


def set_number_of_days(request, number_of_days):
    settings = models.get_settings()
    settings.number_of_days = number_of_days
    log.debug(f"number of days: {number_of_days}")
    settings.save()
    if request.META.get("HTTP_REFERER"):
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        return HttpResponseRedirect(reverse("home"))


def get_summary_of_all_activities(sport_slug=None):
    if sport_slug:
        count = models.Activity.objects.filter(sport__slug=sport_slug).count()
        total_duration = models.Activity.objects.filter(sport__slug=sport_slug).aggregate(Sum("duration"))
        total_distance = models.Activity.objects.filter(sport__slug=sport_slug).aggregate(Sum("distance"))
    else:
        count = models.Activity.objects.all().count()
        total_duration = models.Activity.objects.all().aggregate(Sum("duration"))
        total_distance = models.Activity.objects.all().aggregate(Sum("distance"))
    duration = total_duration["duration__sum"] if total_duration["duration__sum"] else datetime.timedelta(minutes=0)
    distance = int(total_distance["distance__sum"]) if total_distance["distance__sum"] else 0
    return {"count": count, "duration": duration, "distance": distance}


def custom_404_view(request, exception=None):
    return render(None, "lib/404.html", status=404)


def reimport_activities(request):
    messages.info(request, "Running reimport in background...")

    reimporter = Process(
        target=reimport_activity_files,
        args=(models,),
    )
    reimporter.start()

    if request.META.get("HTTP_REFERER"):
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        return HttpResponseRedirect(reverse("settings"))


def get_flat_list_of_pks_of_activities_in_top_awards(
    top_score: int, filter_on_sport: Union[None, str] = None
) -> List[int]:
    top_award_pks = []
    if filter_on_sport:
        sport_slugs = [filter_on_sport]
    else:
        sport_slugs = [
            sport.slug for sport in models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown")
        ]
    for sport in sport_slugs:
        for bs in configuration.best_sections:
            for distance in bs["distances"]:
                top_awards = models.BestSection.objects.filter(
                    activity__sport__slug=sport,
                    activity__evaluates_for_awards=True,
                    kind=bs["kind"],
                    distance=distance,
                ).order_by("-max_value")[:top_score]
                top_award_pks += [award.activity.pk for award in top_awards]
    return list(set(top_award_pks))


def get_bulk_of_rows_for_next_page(request, page: str):
    page = int(page)
    template_name = "lib/row_bulk.html"
    current_url = request.META.get("HTTP_HX_CURRENT_URL")
    sport_slug = None
    if "sport" in current_url:
        sport_slug = current_url.split("/")[-1]

    activities, is_last_page = fetch_row_data_for_page(page_nr=page, sport_slug=sport_slug)
    top_awards = get_flat_list_of_pks_of_activities_in_top_awards(configuration.rank_limit)

    return render(
        request,
        template_name,
        {"activities": activities, "current_page": page + 1, "is_last_page": is_last_page, "top_awards": top_awards},
    )


def fetch_row_data_for_page(page_nr: int, sport_slug=None):
    number_of_rows = configuration.number_of_rows_per_page_in_table
    start = page_nr * number_of_rows
    end = (page_nr + 1) * number_of_rows
    log.debug(f"fetching activity data for table page {page_nr}")
    is_last_page = False
    if sport_slug:
        activities = models.Activity.objects.filter(sport__slug=sport_slug).order_by("-date")
        total_nr_of_activities = activities.count()
        activities = activities[start:end]
    else:
        activities = models.Activity.objects.all().order_by("-date")
        total_nr_of_activities = activities.count()
        activities = activities[start:end]

    # indicate whether the current page is the last one
    if end >= total_nr_of_activities:
        log.debug("reached end of the table")
        is_last_page = True
    return activities, is_last_page
