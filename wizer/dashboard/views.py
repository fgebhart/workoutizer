from django.shortcuts import render
from django.views.generic import View


class DashboardView(View):
    template_name = "dashboard.html"
    def get(self, request):
        return render(request, self.template_name)



class ActivityView(View):
    template_name = "activity.html"
    def get(self, request):
        return render(request, self.template_name)