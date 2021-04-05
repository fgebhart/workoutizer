from django.urls import path
from django.urls import re_path

from wkz import views
from wkz import activity_views
from wkz import sport_views
from wkz import awards_views
from wkz import api


urlpatterns = [
    # home Dashboard
    path("", views.DashboardView.as_view(), name="home"),
    path("set_number_of_days/<slug:number_of_days>", views.set_number_of_days, name="set-number-of-days"),
    path("activities_page/<slug:page>", views.get_bulk_of_rows_for_next_page, name="activities-page"),
    # Settings
    path("settings/", views.settings_view, name="settings"),
    path("settings/reimport", views.reimport_activities, name="reimport"),
    # Help
    path("help/", views.HelpView.as_view(), name="help"),
    # Activities
    path("activity/<slug:activity_id>", activity_views.ActivityView.as_view(), name="activity"),
    path("activity/<slug:activity_id>/edit/", activity_views.edit_activity_view, name="edit-activity"),
    path("activity/<slug:activity_id>/download/", activity_views.download_activity, name="download-activity"),
    path("add-activity/", activity_views.add_activity_view, name="add-activity"),
    re_path(r"^activity/(?P<pk>\d+)/delete/$", activity_views.ActivityDeleteView.as_view(), name="delete-activity"),
    path("delete-demo-data/", activity_views.DemoActivityDeleteView.as_view(), name="delete-demo-data"),
    # Sports
    path("sport/<slug:sports_name_slug>", sport_views.SportView.as_view(), name="sport"),
    path("sports/", sport_views.SportsView.as_view(), name="sports"),
    path("add-sport/", sport_views.add_sport_view, name="add-sport"),
    path("sport/<slug:sports_name_slug>/edit/", sport_views.edit_sport_view, name="edit-sport"),
    re_path(r"^sport/(?P<slug>[a-zA-Z0-9-]+)/delete/$", sport_views.SportDeleteView.as_view(), name="delete-sport"),
    # Best Sections
    path("awards/", awards_views.AwardsViews.as_view(), name="awards"),
    # Rest API endpoints
    path("mount-device/", api.mount_device_endpoint),
    path("stop/", api.stop_django_server),
    # test page for playground of new frontend
    path("new-frontend/", views.new_frontend, name="new_frontend"),
]
