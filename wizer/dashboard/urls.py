from django.urls import path
from dashboard.views import DashboardView


urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard.html"),
]
