from django.shortcuts import render
from django.views.generic import View


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        return render(request, self.template_name)


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
