import logging

from django.shortcuts import render
from django.views.generic import View, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.contrib import messages
from django.urls import reverse

from wizer.views import MapView, PlotView, get_summary_of_activities, get_all_form_field_ids
from wizer.models import Sport
from wizer.forms import AddSportsForm
from wizer.plotting.plot_history import plot_history

log = logging.getLogger(__name__)


class AllSportsView(View):
    template_name = "sport/all_sports.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('name')
        return render(request, self.template_name, {'sports': sports, 'page': 'all_sports',
                                                    'form_field_ids': get_all_form_field_ids()})


class SportsView(MapView, PlotView):
    template_name = "sport/sport.html"

    def get(self, request, sports_name_slug):
        sport_id = Sport.objects.get(slug=sports_name_slug).id
        activities = self.get_activities(sport_id=sport_id)
        log.debug(f"got sports name: {sports_name_slug}")
        map_context = super(SportsView, self).get(request=request, list_of_activities=activities)
        sports = Sport.objects.all().order_by('name')
        summary = get_summary_of_activities(activities=activities)
        if activities:
            script_history, div_history = plot_history(activities=activities, plotting_style=self.settings.plotting_style)
            map_context['script_history'] = script_history
            map_context['div_history'] = div_history
        try:
            sport = model_to_dict(Sport.objects.get(slug=sports_name_slug))
            sport['slug'] = sports_name_slug
        except ObjectDoesNotExist:
            log.critical("this sport does not exist")
            raise Http404
        return render(request, self.template_name,
                      {**map_context, 'activities': activities, 'sports': sports, 'summary': summary, 'sport': sport,
                       'form_field_ids': get_all_form_field_ids()})


def add_sport_view(request):
    sports = Sport.objects.all().order_by('name')
    if request.method == 'POST':
        form = AddSportsForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            messages.success(request, f"Successfully added '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(reverse('sports'))
        else:
            log.warning(f"form invalid: {form.errors}")
    else:
        form = AddSportsForm()
    return render(request, 'sport/add_sport.html', {'sports': sports, 'form': form, 'page': 'add_sport',
                                                    'form_field_ids': get_all_form_field_ids()})


def edit_sport_view(request, sports_name_slug):
    sports = Sport.objects.all().order_by('name')
    sport = Sport.objects.get(slug=sports_name_slug)
    form = AddSportsForm(request.POST or None, instance=sport)
    if request.method == 'POST':
        if form.is_valid():
            log.debug(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, f"Successfully modified '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(f'/sport/{sport.slug}/edit/')
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, 'sport/edit_sport.html', {'sports': sports, 'sport': sport, 'form': form,
                                                     'form_field_ids': get_all_form_field_ids()})


class SportDeleteView(DeleteView):
    template_name = "sport/sport_confirm_delete.html"
    model = Sport
    slug_field = 'slug'
    success_url = "/sports/"

    def get(self, request, *args, **kwargs):
        sports = Sport.objects.all().order_by('name')
        sport = Sport.objects.get(slug=kwargs['slug'])
        return render(request, self.template_name, {'sports': sports, 'sport': sport,
                                                    'form_field_ids': get_all_form_field_ids()})
