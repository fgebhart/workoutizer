import datetime
import operator

from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pytest

from workoutizer import settings as django_settings
from tests.utils import delayed_assertion
from wkz import models


def test_settings_page__no_demo_activity(live_server, webdriver):
    models.get_settings()
    webdriver.get(live_server.url + reverse("settings"))

    assert webdriver.find_element_by_class_name("navbar-brand").text == "Settings"

    # verify the text of the input field labels
    input_labels = [link.text for link in webdriver.find_elements_by_class_name("col-md-4")]
    assert "Path to Traces Directory " in input_labels
    input_labels.remove("Path to Traces Directory ")
    assert "Path to Garmin Device " in input_labels
    input_labels.remove("Path to Garmin Device ")
    assert "Delete fit Files after Copying  " in input_labels
    input_labels.remove("Delete fit Files after Copying  ")
    # reimport got removed, assert it is not present
    assert "Reimport all Files " not in input_labels
    # verify that the list is empty after remove all given input labels
    assert len(input_labels) == 0

    question_hover = [
        question.get_attribute("data-original-title")
        for question in webdriver.find_elements(By.CLASS_NAME, "fa-question-circle")
    ]
    hover_text = ""
    for text in question_hover:
        hover_text = f"{hover_text} {text}"

    assert "path to a directory which both contains" in hover_text
    assert "the path to a directory in which your" in hover_text
    assert "this option to delete fit files from your" in hover_text

    # verify no demo activity is present
    assert len(models.Activity.objects.filter(is_demo_activity=True)) == 0
    # no delete demo data button present
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.ID, "delete-demo-data")

    # check that "made with love" text is present
    assert (
        f"© {datetime.datetime.now().date().year}, made with by Fabian Gebhart"
        in webdriver.find_element(By.CLASS_NAME, "credits").text
    )


def test_settings_page__demo_activity_present__delete_it(import_demo_data, live_server, webdriver):
    models.get_settings()
    webdriver.get(live_server.url + reverse("settings"))

    assert webdriver.find_element_by_class_name("navbar-brand").text == "Settings"

    # verify no demo activity is present
    assert models.Activity.objects.filter(is_demo_activity=True).count() > 18
    # Demo heading is present
    webdriver.find_element(By.ID, "delete-demo-data")

    # also delete demo activity button is present
    first_delete_button = webdriver.find_element_by_id("delete-demo-data")
    assert first_delete_button.text == "  DELETE"

    # click button to verify demo data gets deleted
    first_delete_button.click()
    assert webdriver.current_url == live_server.url + reverse("delete-demo-data")
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Delete Demo Activities"

    # on the new page find the additional delete button and click it
    second_delete_button = webdriver.find_element_by_class_name("btn-space")
    assert second_delete_button.text == "  DELETE"
    second_delete_button.click()

    # verify that all demo data got deleted
    assert models.Activity.objects.filter(is_demo_activity=True).count() == 0

    # no delete demo data button present
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.ID, "delete-demo-data")


def test_settings_page__edit_and_submit_form(live_server, webdriver):
    # get settings and check that all values are at their default configuration
    settings = models.get_settings()
    assert settings.path_to_trace_dir == django_settings.TRACKS_DIR
    assert settings.path_to_garmin_device == "/run/user/1000/gvfs/"
    assert settings.delete_files_after_import is False
    assert settings.number_of_days == 30

    # go to settings page
    webdriver.get(live_server.url + reverse("settings"))
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Settings"

    # Note, that with using htmx to update the settings form, all fields are submitted once their values got changed

    # modify values by inserting into input fields
    trace_dir_input_field = webdriver.find_element(By.ID, "id_path_to_trace_dir")
    trace_dir_input_field.clear()
    trace_dir_input_field.send_keys("some/dummy/path")
    # basically clicking somewhere else to trigger submitting the change
    webdriver.find_element(By.ID, "navigation").click()

    delayed_assertion(lambda: models.get_settings().path_to_trace_dir, operator.eq, "some/dummy/path")

    garmin_device_input_field = webdriver.find_element(By.ID, "id_path_to_garmin_device")
    garmin_device_input_field.clear()
    garmin_device_input_field.send_keys("garmin/dummy/path")
    webdriver.find_element(By.ID, "navigation").click()
    delayed_assertion(lambda: models.get_settings().path_to_garmin_device, operator.eq, "garmin/dummy/path")

    # got removed, should not be accessible
    with pytest.raises(NoSuchElementException):
        webdriver.find_element_by_css_selector("#id_reimporter_updates_all")
    # verify that the number of days field is not present nor editable
    with pytest.raises(NoSuchElementException):
        webdriver.find_element_by_css_selector("#id_number_of_days")

    # again get settings and check that the values are the once entered above
    settings = models.get_settings()
    assert settings.path_to_trace_dir == "some/dummy/path"
    assert settings.path_to_garmin_device == "garmin/dummy/path"

    # did not get changed, since selenium is not able to click into checkbox (?)
    assert settings.delete_files_after_import is False
    # number of days should not be changed
    assert settings.number_of_days == 30

    # this attribute got removed, so verifying that is does no longer exist
    with pytest.raises(AttributeError):
        assert settings.reimporter_updates_all is True

    # reimport button got removed from settings page
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.ID, "reimport-activities").click()
