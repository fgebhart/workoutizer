import logging

from django.shortcuts import render, render_to_response
from django.views.generic import View
from django.http import HttpResponseRedirect

from bokeh.embed import components

from .models import Sport, Activity, Settings
from .forms import SettingsForm
from .plots import plot_activities


log = logging.getLogger('wizer.views')


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('name')
        activities = Activity.objects.all().order_by("-date")

        script, div = components(plot_activities(activities, number_of_days=60))
        return render_to_response(self.template_name,
                                  {'sports': sports, 'activities': activities, 'script': script, 'div': div})


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
