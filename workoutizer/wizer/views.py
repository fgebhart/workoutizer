from django.shortcuts import render
from django.views.generic import View

from wizer.models import Sport


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        sports = Sport.objects.all().order_by('-id')
        return render(request, self.template_name, {'sports': sports})


class ActivityView(View):
    template_name = "activity/activity.html"

    def get(self, request):
        return render(request, self.template_name)


class AddActivityView(View):
    template_name = "activity/add_activity.html"

    def get(self, request):
        return render(request, self.template_name)


class SportsView(View):
    template_name = "sports/sports.html"

    def get(self, request):
        return render(request, self.template_name)


class AddSportsView(View):
    template_name = "sports/add_sports.html"

    def get(self, request):
        return render(request, self.template_name)
