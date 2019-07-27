from django.urls import path
from django.conf.urls import url
from wizer.views import DashboardView, AllActivitiesView, add_activity_view, SportsView, AllSportsView, add_sport_view,\
    ActivityView, settings_view, edit_activity_view, edit_sport_view, SportDeleteView, ActivityDeleteView

urlpatterns = [
    # home Dashboard
    path('', DashboardView.as_view(), name="home"),

    # Activities
    path('activities/', AllActivitiesView.as_view(), name="activities"),
    path('activity/<slug:activity_id>', ActivityView.as_view(), name="activity"),
    path('activity/<slug:activity_id>/edit/', edit_activity_view, name="edit-activity"),
    path('add-activity/', add_activity_view, name="add-activity"),
    url(r'^activity/(?P<pk>\d+)/delete/$', ActivityDeleteView.as_view(), name="delete-activity"),

    # Sports
    path('sport/<slug:sports_name_slug>', SportsView.as_view(), name="sports"),
    path('sports/', AllSportsView.as_view(), name="sports"),
    path('add-sport/', add_sport_view, name="add-sport"),
    path('sport/<slug:sports_name_slug>/edit/', edit_sport_view, name="edit-sport"),
    url(r'^sport/(?P<slug>[a-zA-Z0-9-]+)/delete/$', SportDeleteView.as_view(), name="delete-sport"),

    # Settings
    path('settings/', settings_view, name="settings"),

]
