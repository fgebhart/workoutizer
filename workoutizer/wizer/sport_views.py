import logging

from django.shortcuts import render
from django.views.generic import View, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from .views import MapView
from .models import Sport, Activity
from .forms import AddSportsForm
from .plots import create_plot

log = logging.getLogger('wizer.sport_views')


class AllSportsView(View):
    template_name = "sport/all_sports.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('name')
        return render(request, self.template_name, {'sports': sports})


class SportsView(MapView):
    template_name = "sport/sport.html"

    def get(self, request, sports_name_slug):
        log.debug(f"got sports name: {sports_name_slug}")
        log.debug(f"request in sports view: {request.user}")
        log.debug(f"sports_name_slug: {sports_name_slug}")
        sport_id = Sport.objects.get(slug=sports_name_slug).id
        log.debug(f"sport id: {sport_id}")
        activities = Activity.objects.filter(sport=sport_id).order_by("-date")
        log.debug(f"got activities: {activities}")
        context = super(SportsView, self).get(request=request, list_of_activities=activities)
        context['activities'] = activities
        context['sports'] = Sport.objects.all().order_by('name')
        script, div = create_plot(activities=activities)
        context['script'] = script
        context['div'] = div
        try:
            sport = model_to_dict(Sport.objects.get(slug=sports_name_slug))
            sport['slug'] = sports_name_slug
            context['sport'] = sport
        except ObjectDoesNotExist:
            log.critical("this sport does not exist")
            raise Http404
        return render(request, self.template_name, context)


def add_sport_view(request):
    sports = Sport.objects.all().order_by('name')
    if request.method == 'POST':
        form = AddSportsForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            return HttpResponseRedirect('/sports')
        else:
            log.warning(f"form invalid: {form.errors}")
    else:
        form = AddSportsForm()
    return render(request, 'sport/add_sport.html', {'sports': sports, 'form': form})


def edit_sport_view(request, sports_name_slug):
    sports = Sport.objects.all().order_by('name')
    sport = Sport.objects.get(slug=sports_name_slug)
    form = AddSportsForm(request.POST or None, instance=sport)
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            return HttpResponseRedirect(f'/sport/{sport.slug}/edit/')
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, 'sport/edit_sport.html', {'sports': sports, 'sport': sport, 'form': form})


class SportDeleteView(DeleteView):
    template_name = "sport/sport_confirm_delete.html"
    model = Sport
    slug_field = 'slug'
    success_url = "/sports/"

    def get(self, request, *args, **kwargs):
        log.debug(f"kwargs: {kwargs}")
        sports = Sport.objects.all().order_by('name')
        sport = Sport.objects.get(slug=kwargs['slug'])
        log.debug(f"my sports: {sports}")
        log.debug(f"my sport: {sport}")
        return render(request, self.template_name, {'sports': sports, 'sport': sport})
