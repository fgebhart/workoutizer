import logging

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from bokeh.embed import components

from .models import Sport, Activity, Settings
from .forms import SettingsForm, DaysDropDown
from .plots import plot_activities

log = logging.getLogger('wizer.views')


class DashboardView(View):
    template_name = "dashboard.html"
    sports = Sport.objects.all().order_by('name')
    activities = Activity.objects.all().order_by("-date")
    number_of_days = None
    days_choices = None
    settings = None
    div = None
    script = None

    def get_days_config(self, request):
        self.settings = Settings.objects.get(user_id=request.user.id)
        self.number_of_days = self.settings.number_of_days
        self.days_choices = Settings.days_choices

    def create_plot(self):
        try:
            self.script, self.div = components(
                plot_activities(self.activities, self.sports, number_of_days=self.number_of_days))
        except AttributeError as e:
            log.error(f"Error rendering plot. Check if activity data is correct: {e}", exc_info=True)
            self.script = self.div = "Error rendering Plot"

    def get(self, request):
        self.sports = Sport.objects.all().order_by('name')
        self.activities = Activity.objects.all().order_by("-date")
        self.get_days_config(request)
        self.create_plot()
        form = DaysDropDown(request.POST or None, instance=self.settings)
        return render(request, self.template_name,
                      {'form': form, 'sports': self.sports, 'activities': self.activities,
                       'script': self.script, 'div': self.div, 'days': self.number_of_days,
                       'choices': self.days_choices})

    def post(self, request):
        self.get_days_config(request)
        self.create_plot()
        form = DaysDropDown(request.POST or None, instance=self.settings)
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            return HttpResponseRedirect("/")
        else:
            log.warning(f"form invalid, form: \n {form.errors}")
        return render(request, self.template_name,
                      {'form': form, 'sports': self.sports, 'activities': self.activities,
                       'script': self.script, 'div': self.div, 'days': self.number_of_days,
                       'choices': self.days_choices})


def settings_view(request):
    sports = Sport.objects.all().order_by('name')
    user_id = request.user.id
    settings = Settings.objects.get(user_id=user_id)
    form = SettingsForm(request.POST or None, instance=settings)
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            return HttpResponseRedirect('/settings')
        else:
            log.warning(f"form invalid")
    return render(request, "settings.html", {'sports': sports, 'form': form, 'settings': settings})
