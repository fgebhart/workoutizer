from django.shortcuts import render
from django.views.generic import View


class DashboardView(View):
    template_name = "dashboard.html"
    def get(self, request):

        print("get...")
        return render(request, self.template_name)

