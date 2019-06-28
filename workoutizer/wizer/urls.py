from django.urls import path
from wizer.views import DashboardView, AllActivitiesView, add_activity_view, SportsView, AllSportsView, add_sport_view,\
    ActivityView, settings_view, edit_activity_view

urlpatterns = [
    path('', DashboardView.as_view(), name="home"),
    path('activities/', AllActivitiesView.as_view(), name="activities"),
    path('settings/', settings_view, name="settings"),
    path('activity/<slug:activity_id>', ActivityView.as_view(), name="activity"),
    path('activity/<slug:activity_id>/edit/', edit_activity_view, name="edit-activity"),
    path('add-activity/', add_activity_view, name="add-activity"),
    path('sport/<slug:sports_name_slug>', SportsView.as_view(), name="sports"),
    path('sports/', AllSportsView.as_view(), name="sports"),
    path('add-sport/', add_sport_view, name="add-sport"),
]
