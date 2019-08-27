from django.urls import path
from django.conf.urls import url
from wizer.views import DashboardView, settings_view, set_number_of_days
from wizer.activity_views import add_activity_view, edit_activity_view, ActivityDeleteView, ActivityView
from wizer.sport_views import edit_sport_view, SportDeleteView, SportsView, AllSportsView, add_sport_view

urlpatterns = [
    # home Dashboard
    path('', DashboardView.as_view(), name="home"),
    path('set_number_of_days/<slug:number_of_days>', set_number_of_days, name="set-number-of-days"),

    # Activities
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
