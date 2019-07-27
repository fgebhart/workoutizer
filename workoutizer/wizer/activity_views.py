import logging

from django.shortcuts import render
from django.views.generic import View, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from .models import Sport, Activity
from .forms import AddActivityForm, EditActivityForm


log = logging.getLogger('wizer.activity_views')


class ActivityView(View):
    template_name = "activity/activity.html"
    def get(self, request, activity_id):
        sports = Sport.objects.all().order_by('name')
        log.error(f"got activity_id: {activity_id}")
        try:
            activity = Activity.objects.get(id=activity_id)
            log.debug(f"passing activity: {activity} from model to view")
        except ObjectDoesNotExist:
            log.critical("this activity does not exist")
            raise Http404
        return render(request, self.template_name, {'activity': activity, 'sports': sports})


def add_activity_view(request):
    sports = Sport.objects.all().order_by('name')
    if request.method == 'POST':
        form = AddActivityForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            return HttpResponseRedirect('/')
    else:
        form = AddActivityForm()
    return render(request, 'activity/add_activity.html', {'sports': sports, 'form': form})


def edit_activity_view(request, activity_id):
    sports = Sport.objects.all().order_by('name')
    log.debug(f"querying for activity id: {activity_id}")
    activity = Activity.objects.get(id=activity_id)
    form = EditActivityForm(request.POST or None, instance=activity)
    log.debug(f"got form: {form}")
    if request.method == 'POST':
        if form.is_valid():
            log.info(f"got valid form: {form.cleaned_data}")
            form.save()
            return HttpResponseRedirect(f"/activity/{activity_id}")
        else:
            log.warning(f"form invalid")
    return render(request, 'activity/edit_activity.html', {'form': form, 'sports': sports, 'activity': activity})


class ActivityDeleteView(DeleteView):
    template_name = "activity/activity_confirm_delete.html"
    model = Activity
    slug_field = 'activity_id'
    success_url = "/"
