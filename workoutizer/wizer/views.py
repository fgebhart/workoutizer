import logging

from django.shortcuts import render
from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from .models import Sport, Activity
from .forms import AddSportsForm, AddActivityForm
from .gpx_converter import GPXConverter

log = logging.getLogger(__name__)


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        activities = Activity.objects.all()
        return render(request, self.template_name, {'sports': sports, 'activities': activities})


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
        gjson = GPXConverter(path_to_gpx='../../../tracks/2019-05-30_13-31-01.gpx', activity="cycling")
        trace = gjson.get_geojson()
        track_parameters = gjson.track_params
        log.debug(f"my track: {trace}")
        try:
            activity = model_to_dict(Activity.objects.get(id=activity_id))
            log.error(f"database has activity: {activity}")
        except ObjectDoesNotExist:
            log.critical("this activity does not exist")
            raise Http404

        return render(request, self.template_name, {'activity': activity,
                                                    'sports': sports,
                                                    'trace': trace,
                                                    'track_params': track_parameters})


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
        form = AddActivityForm()
    return render(request, 'add_activity.html', {'sports': sports, 'form': form})


def add_sport_view(request):
    sports = Sport.objects.all().order_by('id')
    if request.method == 'POST':
        print("got POST")
        form = AddSportsForm(request.POST)
        print(f"form: {form}")
        if form.is_valid():
            print(f"got form: {form.cleaned_data}")
            instance = form.save()
            instance.save()
            return HttpResponseRedirect('/sports/')
    else:
        form = AddSportsForm()
    return render(request, 'add_sport.html', {'sports': sports, 'form': form})
