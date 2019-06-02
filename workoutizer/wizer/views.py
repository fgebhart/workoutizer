import logging
from json import loads, dumps

from django.shortcuts import render
from django.views.generic import View
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from .models import Sport, Activity
from .forms import AddSportsForm
from .gpx_converter import GPXConverter
from .geojson_dict import mydict

log = logging.getLogger(__name__)


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        activities = Activity.objects.all()
        return render(request, self.template_name, {'sports': sports, 'activities': activities})


class ActivityView(View):
    template_name = "activity/activity.html"

    def get(self, request, activity_id):
        sports = Sport.objects.all().order_by('id')
        log.error(f"got activity_id: {activity_id}")
        gjson = GPXConverter(path_to_gpx='../../../tracks/2019-05-30_13-31-01.gpx', activity="cycling")
        track = gjson.get_geojson()
        print(f"my track: {track}")

        try:
            activity = model_to_dict(Activity.objects.get(id=activity_id))
            log.error(f"database has activity: {activity}")
            return render(request, self.template_name, {'activity': activity, 'sports': sports, 'track': track})
        except ObjectDoesNotExist:
            log.critical("this activity does not exist")
            raise Http404


class AddActivityView(View):
    template_name = "activity/add_activity.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        return render(request, self.template_name, {'sports': sports})


class SportsView(View):
    template_name = "sports/sports.html"

    def get(self, request, sports_name_slug):
        log.error(f"got sports name: {sports_name_slug}")
        sport_id = Sport.objects.get(slug=sports_name_slug).id
        activities = Activity.objects.filter(sport=sport_id)
        sports = Sport.objects.all().order_by('id')
        try:
            sport = model_to_dict(Sport.objects.get(slug=sports_name_slug))
            log.error(f"database has sport: {sport}")
            return render(request, self.template_name, {'activities': activities, 'sport': sport, 'sports': sports})
        except ObjectDoesNotExist:
            log.critical("this sport does not exist")
            raise Http404


class AddSportsView(View):
    template_name = "sports/add_sports.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('id')
        return render(request, self.template_name, {'sports': sports})

    def post(self, request):
        form = AddSportsForm(request.POST)
        if form.is_valid():
            print(f"got form: {form.cleaned_data}")
            sports_name = form.cleaned_data['sports_name']
            print(f"sports_name: {sports_name}")
