from django.urls import path
from wizer.views import DashboardView, ActivityView, AddActivityView, SportsView, AddSportsView, AllSportsView, add_sports_view

urlpatterns = [
    path('', DashboardView.as_view(), name="home"),
    path('activity/<slug:activity_id>', ActivityView.as_view(), name="activity"),
    path('add-activity/', AddActivityView.as_view(), name="add-activity"),
    path('sports/<slug:sports_name_slug>', SportsView.as_view(), name="sports"),
    path('sports/', AllSportsView.as_view(), name="sports"),
    path('add-sports/', add_sports_view, name="add-sports"),
]
