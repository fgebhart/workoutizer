import os
import logging
import datetime

from django.shortcuts import render
from django.views.generic import DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.forms import modelformset_factory
import pytz

from workoutizer import settings as django_settings
from wkz.views import MapView, get_all_form_field_ids
from wkz.awards_views import get_top_awards_for_one_sport, get_ascent_ranking_of_activity
from wkz.models import Sport, Activity, Lap, BestSection
from wkz.forms import AddActivityForm, EditActivityForm, DATETIMEPICKER_FORMAT
from wkz.file_helper.gpx_exporter import save_activity_to_gpx_file
from wkz.plotting.plot_time_series import plot_time_series
from wkz.best_sections.generic import activity_suitable_for_awards
from wkz import configuration as cfg

log = logging.getLogger(__name__)


class ActivityView(MapView):
    template_name = "activity/activity.html"

    def get(self, request, activity_id):
        activity = Activity.objects.get(id=activity_id)
        context = super(ActivityView, self).get(request=request, list_of_activities=[activity])
        settings = context["settings"]
        setattr(settings, "every_nth_value", cfg.every_nth_value)
        context["settings"] = settings
        activity_context = {
            "sports": Sport.objects.all().order_by("name"),
            "activity": activity,
            "form_field_ids": get_all_form_field_ids(),
            "fastest_sections": BestSection.objects.filter(activity=activity, kind="fastest"),
            "climb_sections": BestSection.objects.filter(activity=activity, kind="climb"),
            "page_name": activity.name,
            "is_activity_page": True,
        }
        if activity.trace_file:
            script_time_series, div_time_series, number_of_plots = plot_time_series(activity)
            activity_context["script_time_series"] = script_time_series
            activity_context["div_time_series"] = div_time_series
            activity_context["map_height"] = _get_map_height(number_of_plots)
        laps = Lap.objects.filter(trace=activity.trace_file, trigger="manual")
        if laps:
            activity_context["laps"] = laps
        activity_context["evaluates_for_awards"] = False
        if activity_suitable_for_awards(activity):
            activity_context["top_fastest_awards"] = get_top_awards_for_one_sport(
                sport=activity.sport, top_score=cfg.rank_limit, kinds=["fastest"]
            )
            activity_context["top_climb_awards"] = get_top_awards_for_one_sport(
                sport=activity.sport, top_score=cfg.rank_limit, kinds=["climb"]
            )
            activity_context["ascent_awards_ranking"] = get_ascent_ranking_of_activity(activity)
            activity_context["evaluates_for_awards"] = True
        return render(request, self.template_name, {**context, **activity_context})


def _get_map_height(number_of_plots: int) -> int:
    height = number_of_plots * 120 + 40
    if height < 400:
        return 400
    else:
        return height


def add_activity_view(request):
    sports = Sport.objects.all().order_by("name")
    if request.method == "POST":
        form = AddActivityForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            messages.success(request, f"Successfully added '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(reverse("home"))
        else:
            log.warning(f"form invalid: {form.errors}")
    else:
        form = AddActivityForm(initial={"date": str(datetime.datetime.now().strftime(DATETIMEPICKER_FORMAT))})
    return render(
        request,
        "activity/add_activity.html",
        {"sports": sports, "form": form, "form_field_ids": get_all_form_field_ids(), "page_name": "Add Activity"},
    )


def edit_activity_view(request, activity_id):
    form_field_ids = get_all_form_field_ids()
    sports = Sport.objects.all().order_by("name")
    activity = Activity.objects.get(id=activity_id)
    date = activity.date.astimezone(pytz.timezone(django_settings.TIME_ZONE))
    date = str(date.strftime(DATETIMEPICKER_FORMAT))
    activity_form = EditActivityForm(request.POST or None, instance=activity, initial={"date": date})
    laps = Lap.objects.filter(trace=activity.trace_file, trigger="manual")
    has_laps = True if laps else False
    if has_laps:
        LapFormSet = modelformset_factory(Lap, fields=("label",))
        formset = LapFormSet(request.POST or None, queryset=laps)
        form_field_ids = _add_formset_field_ids(form_field_ids, formset)
    else:
        formset = None
    if request.method == "POST":
        if activity_form.is_valid():
            log.debug(f"got valid activity_form: {activity_form.cleaned_data}")
            activity_form.save()
            if has_laps:
                if formset.is_valid():
                    formset.save()
            messages.success(request, f"Successfully modified '{activity_form.cleaned_data['name']}'")
            return HttpResponseRedirect(f"/activity/{activity_id}")
        else:
            log.warning(f"form invalid: {activity_form.errors}")
            if has_laps:
                log.warning(f"form invalid: {activity_form.errors}")
    return render(
        request,
        "activity/edit_activity.html",
        {
            "form": activity_form,
            "sports": sports,
            "activity": activity,
            "formset": formset,
            "has_laps": has_laps,
            "form_field_ids": form_field_ids,
            "page_name": f"Edit Activity: {activity.name}",
        },
    )


def _add_formset_field_ids(form_field_ids, formset):
    """
    Add all input fields of a given form set to the list of all field ids in order to avoid
    keyboard navigation while entering text in form fields.
    """

    for i, form in enumerate(formset):
        for field in form.base_fields.keys():
            field = f"id_form-{i}-{field}"
            form_field_ids.append(field)
    return form_field_ids


def download_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    path = save_activity_to_gpx_file(activity=activity)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "inline; filename=" + os.path.basename(path)
            return response
    raise Http404


class ActivityDeleteView(DeleteView):
    template_name = "activity/activity_confirm_delete.html"
    model = Activity
    slug_field = "activity_id"
    success_url = "/"

    def get(self, request, *args, **kwargs):
        sports = Sport.objects.all().order_by("name")
        activity = Activity.objects.get(id=kwargs["pk"])
        return render(
            request,
            self.template_name,
            {
                "sports": sports,
                "activity": activity,
                "form_field_ids": get_all_form_field_ids(),
                "page_name": f"Delete Activity: {activity.name}",
            },
        )


class DemoActivityDeleteView(DeleteView):
    template_name = "activity/demo_activity_confirm_delete.html"
    activities = Activity.objects.filter(is_demo_activity=True)

    def get(self, request, *args, **kwargs):
        sports = Sport.objects.all().order_by("name")
        log.debug(f"activities to be deleted: {self.activities}")
        return render(
            request,
            self.template_name,
            {
                "sports": sports,
                "activities": self.activities,
                "form_field_ids": get_all_form_field_ids(),
                "page_name": "Delete Demo Activities",
            },
        )

    def post(self, request, *args, **kwargs):
        log.debug(f"deleting: {self.activities}")
        for activity in self.activities:
            activity.delete()
        log.info("deleted demo activities")
        return HttpResponseRedirect(reverse("home"))
