import logging
import json
import datetime
from typing import List, Dict, Union

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.contrib import messages
from multiprocessing import Process
from django.urls import reverse
from django.utils import timezone

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
        log.debug(f"got list_of_activity_ids: {list_of_activities}")
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

    def get_activities(self, sport_id=None):
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
        self.sports = models.Sport.objects.all().order_by("name")
        activities = self.get_activities()
        summary = get_summary_of_activities(activities=activities)
        top_awards = get_flat_list_of_pks_of_activities_in_top_awards(configuration.rank_limit)
        context = {
            "sports": self.sports,
            "activities": activities,
            "days": self.number_of_days,
            "choices": self.days_choices,
            "summary": summary,
            "page": "dashboard",
            "form_field_ids": get_all_form_field_ids(),
            "top_awards": top_awards,
        }
        if activities:
            script_history, div_history = plot_history(
                activities=activities, sport_model=models.Sport, settings_model=models.Settings
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
            }
            return render(request, self.template_name, {**context, **plotting_context})
        else:
            log.warning("no activities found...")
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


def get_summary_of_activities(activities):
    total_duration = datetime.timedelta(minutes=0)
    for a in activities:
        total_duration += a.duration
    log.debug(f"total duration of selected activities: {total_duration}")
    return {"count": len(activities), "duration": total_duration, "distance": int(sum(n.distance for n in activities))}


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


class BestSectionsView(WKZView):
    template_name = "best_sections.html"

    def get(self, request):
        self.context["page"] = "awards"
        top_awards = get_top_awards_for_all_sports(top_score=configuration.rank_limit)
        self.context["top_awards"] = top_awards
        return render(request, template_name=self.template_name, context=self.context)


def _get_best_sections_of_sport_and_distance(
    sport: models.Sport, distance: int, top_score: int
) -> List[models.BestSection]:
    awards_per_distance = list(
        models.BestSection.objects.filter(
            activity__sport=sport,
            activity__evaluates_for_awards=True,
            section_distance=distance,
            section_type="fastest",
        ).order_by("-max_value")[:top_score]
    )
    return awards_per_distance


def get_top_awards_for_one_sport(sport: models.Sport, top_score: int) -> List[models.BestSection]:
    awards = []
    for distance in configuration.fastest_sections:
        awards_per_distance = _get_best_sections_of_sport_and_distance(sport, distance, top_score)
        for rank, section in enumerate(awards_per_distance):
            setattr(section, "rank", rank + 1)
        if awards_per_distance:
            awards += awards_per_distance
    return awards


def get_top_awards_for_all_sports(top_score: int) -> Dict[models.Sport, List[models.BestSection]]:
    top_awards = {}
    for sport in models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown").order_by("name"):
        awards = get_top_awards_for_one_sport(sport, top_score)
        if awards:
            top_awards[sport] = awards
    return top_awards


def get_flat_list_of_pks_of_activities_in_top_awards(
    top_score: int, filter_on_sport: Union[None, models.Sport] = None
) -> List[int]:
    top_awards = []
    sports = models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown").order_by("name")
    if filter_on_sport:
        sports = sports.filter(slug=filter_on_sport)
    for sport in sports:
        for distance in configuration.fastest_sections:
            awards_per_distance = _get_best_sections_of_sport_and_distance(sport, distance, top_score)
            # create list of primary keys of activities in which are in top scores
            awards_per_distance = [section.activity.pk for section in awards_per_distance]
            if awards_per_distance:
                top_awards += awards_per_distance
    return top_awards
