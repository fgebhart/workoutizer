import datetime

from wizer.forms import EditSettingsForm, AddSportsForm, AddActivityForm, EditActivityForm


def test_edit_settings_form():
    form_data = {
        "path_to_trace_dir": "/home/pi/traces/",
        "path_to_garmin_device": "/home/pi/traces/",
        "file_checker_interval": 90,
        "number_of_days": 30,
        "trace_width": 1.0,
        "trace_opacity": 0.7,
        "plotting_style": "bar",
        "reimporter_updates_all": False,
        "delete_files_after_import": False,
    }
    form = EditSettingsForm(data=form_data)
    assert form.is_valid() is True


def test_add_sport_form(db):
    form_data = {
        "name": "Running",
        "color": "#060087",
        "icon": "running",
    }
    form = AddSportsForm(data=form_data)
    assert form.is_valid() is True


def test_add_and_edit_activity_form(db, sport):
    form_data = {
        "name": "Running",
        "sport": sport,
        "date": datetime.date.today(),
        "duration": datetime.timedelta(minutes=30),
        "distance": 5.2,
        "description": "some super sport",
    }
    form = AddActivityForm(data=form_data)
    assert form.is_valid() is True

    form = EditActivityForm(data=form_data)
    assert form.is_valid() is True

