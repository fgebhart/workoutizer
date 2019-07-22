import logging

from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from bokeh.embed import components

from .models import Sport, Activity, Settings
from .forms import AddSportsForm, AddActivityForm, SettingsForm, EditActivityForm
from .plots import plot_activities


log = logging.getLogger('wizer.views')


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        activities = Activity.objects.all().order_by("-date")

        script, div = components(plot_activities(activities, number_of_days=60))
        return render_to_response(self.template_name,
                                  {'sports': sports, 'activities': activities, 'script': script, 'div': div})


class AllActivitiesView(View):
    template_name = "all_activities.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        activities = Activity.objects.all()
        return render(request, self.template_name, {'sports': sports, 'activities': activities})


class AllSportsView(View):
    template_name = "all_sports.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        return render(request, self.template_name, {'sports': sports})


class ActivityView(View):
    template_name = "activity.html"

    def get(self, request, activity_id):
        sports = Sport.objects.all().order_by('id')
        log.error(f"got activity_id: {activity_id}")
        try:
            activity = Activity.objects.get(id=activity_id)
            log.debug(f"passing activity: {activity} from model to view")
        except ObjectDoesNotExist:
            log.critical("this activity does not exist")
            raise Http404
        return render(request, self.template_name, {'activity': activity, 'sports': sports})


class SportsView(View):
    template_name = "sport.html"

    def get(self, request, sports_name_slug):
        log.error(f"got sports name: {sports_name_slug}")
        sport_id = Sport.objects.get(slug=sports_name_slug).id
        activities = Activity.objects.filter(sport=sport_id)
        sports = Sport.objects.all().order_by('id')
        try:
            sport = model_to_dict(Sport.objects.get(slug=sports_name_slug))
            log.error(f"database has sport: {sport}")
        except ObjectDoesNotExist:
            log.critical("this sport does not exist")
            raise Http404

        return render(request, self.template_name, {'activities': activities, 'sport': sport, 'sports': sports})


def add_activity_view(request):
    sports = Sport.objects.all().order_by('id')
    print(f"got sports: {sports}")
    if request.method == 'POST':
        print("got POST")
        form = AddActivityForm(request.POST)
        print(f"form: {form}")
        if form.is_valid():
            print(f"got form: {form.cleaned_data}")
            instance = form.save()
            instance.save()
            return HttpResponseRedirect('/')
    else:
        print("got GET")
        form = AddActivityForm()
    return render(request, 'add_activity.html', {'sports': sports, 'form': form})


def edit_activity_view(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    sports = Sport.objects.all().order_by('id')
    instance = get_object_or_404(Activity, id=activity_id)
    form = EditActivityForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('next_view')
    return render(request, 'edit_activity.html', {'form': form, 'sports': sports, 'activity': activity})

#
# def edit_activity_view(request, activity_id):  # TODO this func and template needs rework
#     sports = Sport.objects.all().order_by('id')
#     activity = Activity.objects.get(id=activity_id)
#     if request.method == 'POST':
#         log.info(f"got post with request {request.POST}")
#         form = EditActivityForm(request.POST or None)
#         log.debug(f"form: {form}")
#         if form.is_valid():
#             log.debug(f"valid form: {form.cleaned_data}")
#             instance = form.save()
#             instance.save()
#             return HttpResponseRedirect(f'/activity/{activity.id}/edit/')
#     else:
#         form = EditActivityForm()
#     return render(request, 'edit_activity.html', {'activity': activity, 'sports': sports, 'form': form})


def add_sport_view(request):
    sports = Sport.objects.all().order_by('id')
    if request.method == 'POST':
        form = AddSportsForm(request.POST)
        print(f"form: {form}")
        if form.is_valid():
            print(f"got form: {form.cleaned_data}")
            instance = form.save()
            instance.save()
            return HttpResponseRedirect('/sports')
        else:
            log.warning(f"form invalid")
    else:
        form = AddSportsForm()
    return render(request, 'add_sport.html', {'sports': sports, 'form': form})


def settings_view(request):
    sports = Sport.objects.all().order_by('id')
    user_id = request.user.id
    settings = Settings.objects.get(user_id=user_id)
    form = SettingsForm(request.POST or None, instance=settings)
    log.debug(f"got form:\n{form}")
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            # instance.save()
            return HttpResponseRedirect('/settings')
        else:
            log.warning(f"form invalid")
    return render(request, "settings.html", {'sports': sports, 'form': form, 'settings': settings})
