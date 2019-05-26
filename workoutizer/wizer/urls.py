from django.urls import path
from wizer.views import DashboardView, ActivityView, AddActivityView, SportsView, AddSportsView


urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard.html"),
    path('activity', ActivityView.as_view(), name="activity/activity.html"),
    path('activity/add', AddActivityView.as_view(), name="activity/add_activity.html"),
    path('sports', SportsView.as_view(), name="sports/sports.html"),
    path('sports/add', AddSportsView.as_view(), name="sports/add_sports.html"),
]
