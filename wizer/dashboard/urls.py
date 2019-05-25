from django.urls import path
from dashboard.views import DashboardView, ActivityView


urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard.html"),
    path('activity', ActivityView.as_view(), name="activity.html"),
]
