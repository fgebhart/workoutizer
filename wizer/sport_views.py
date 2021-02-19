import logging

import pandas as pd
from django.shortcuts import render
from django.views.generic import View, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.contrib import messages
from django.urls import reverse

from wizer.views import (
    MapView,
    PlotView,
    get_summary_of_all_activities,
    get_all_form_field_ids,
    get_flat_list_of_pks_of_activities_in_top_awards,
)
from wizer import models
from wizer.forms import AddSportsForm
from wizer.plotting.plot_history import plot_history
from wizer import configuration
from wizer.tools.utils import remove_microseconds

log = logging.getLogger(__name__)


class AllSportsView(View):
    template_name = "sport/all_sports.html"

    def get(self, request):
        sports = models.Sport.objects.all().order_by("name")
        sport_data = {}
        for sport in sports:
            if sport.name not in configuration.protected_sports:
                activities_df = pd.DataFrame(
                    list(models.Activity.objects.filter(sport=sport.id).values("duration", "distance"))
                )
                setattr(sport, "total_count", len(activities_df))
                if activities_df.empty:
                    setattr(sport, "total_distance", 0)
                    setattr(sport, "total_duration", 0)
                else:
                    setattr(sport, "total_distance", round(activities_df["distance"].sum(), 2))
                    setattr(sport, "total_duration", remove_microseconds(activities_df["duration"].sum()))
        return render(
            request,
            self.template_name,
            {"sports": sports, "page": "all_sports", "form_field_ids": get_all_form_field_ids(), **sport_data},
        )


class SportsView(MapView, PlotView):
    template_name = "sport/sport.html"

    def get(self, request, sports_name_slug):
        log.debug(f"got sports name: {sports_name_slug}")
        settings = models.get_settings()
        if sports_name_slug == "undefined":
            log.warning("could not find sport - redirecting to home")
            return HttpResponseRedirect(reverse("home"))
        sport = models.Sport.objects.get(slug=sports_name_slug)
        activities = self.get_activity_data_for_plots(sport_id=sport.id)
        context = {}
        sports = models.Sport.objects.all().order_by("name")
        summary = get_summary_of_all_activities(sport_slug=sports_name_slug)
        if activities:
            script_history, div_history = plot_history(
                activities=activities,
                sport_model=models.Sport,
                number_of_days=settings.number_of_days,
            )
            context["script_history"] = script_history
            context["div_history"] = div_history
            context["activities_selected_for_plot"] = True
        else:
            context["activities_selected_for_plot"] = False
        map_context = super(SportsView, self).get(request=request, list_of_activities=activities)
        if sport.evaluates_for_awards:
            top_awards = get_flat_list_of_pks_of_activities_in_top_awards(configuration.rank_limit, sports_name_slug)
            context["top_awards"] = top_awards
        try:
            sport = model_to_dict(models.Sport.objects.get(slug=sports_name_slug))
            sport["slug"] = sports_name_slug
        except ObjectDoesNotExist:
            log.critical("this sport does not exist")
            raise Http404
        page = 0
        return render(
            request,
            self.template_name,
            {
                **map_context,
                **context,
                "current_page": page,
                "is_last_page": False,
                "sports": sports,
                "summary": summary,
                "sport": sport,
                "form_field_ids": get_all_form_field_ids(),
            },
        )


def add_sport_view(request):
    sports = models.Sport.objects.all().order_by("name")
    if request.method == "POST":
        form = AddSportsForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            messages.success(request, f"Successfully added '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(reverse("sports"))
        else:
            log.warning(f"form invalid: {form.errors}")
    else:
        form = AddSportsForm()
    return render(
        request,
        "sport/add_sport.html",
        {"sports": sports, "form": form, "page": "add_sport", "form_field_ids": get_all_form_field_ids()},
    )


def edit_sport_view(request, sports_name_slug):
    sports = models.Sport.objects.all().order_by("name")
    sport = models.Sport.objects.get(slug=sports_name_slug)
    if sport.name in configuration.protected_sports:
        messages.warning(request, f"Can't edit sport '{sport.name}'")
        return HttpResponseRedirect(f"/sport/{sport.slug}")
    form = AddSportsForm(request.POST or None, instance=sport)
    if request.method == "POST":
        if form.is_valid():
            log.debug(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, f"Successfully modified '{form.cleaned_data['name']}' Sport")
            return HttpResponseRedirect(f"/sport/{sport.slug}/edit/")
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(
        request,
        "sport/edit_sport.html",
        {"sports": sports, "sport": sport, "form": form, "form_field_ids": get_all_form_field_ids()},
    )


class SportDeleteView(DeleteView):
    template_name = "sport/sport_confirm_delete.html"
    model = models.Sport
    slug_field = "slug"
    success_url = "/sports/"

    def get(self, request, *args, **kwargs):
        sports = models.Sport.objects.all().order_by("name")
        sport = models.Sport.objects.get(slug=kwargs["slug"])
        if sport.name in configuration.protected_sports:
            messages.warning(request, f"Can't delete sport '{sport.name}'")
            return HttpResponseRedirect(f"/sport/{sport.slug}")
        return render(
            request, self.template_name, {"sports": sports, "sport": sport, "form_field_ids": get_all_form_field_ids()}
        )
