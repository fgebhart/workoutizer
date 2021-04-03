from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
from workoutizer import settings as django_settings

import pytest

from wizer import models


def test_settings_page__no_demo_activity(live_server, webdriver):
    models.get_settings()
    webdriver.get(live_server.url + reverse("settings"))

    assert webdriver.find_element_by_tag_name("h3").text == "Settings"

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h5")]
    assert "File Importer" in headings
    assert "Reimporter" in headings

    # verify the text of the input field labels
    input_labels = [link.text for link in webdriver.find_elements_by_class_name("col-sm-4")]
    assert "Path to Traces Directory:" in input_labels
    input_labels.remove("Path to Traces Directory:")
    assert "Path to Garmin Device:" in input_labels
    input_labels.remove("Path to Garmin Device:")
    assert "Delete fit Files after Copying:" in input_labels
    input_labels.remove("Delete fit Files after Copying:")
    assert "Reimport all Files:" in input_labels
    input_labels.remove("Reimport all Files:")
    # verify that the list is empty after remove all given input labels
    assert len(input_labels) == 0

    # verify no demo activity is present
    assert len(models.Activity.objects.filter(is_demo_activity=True)) == 0
    # no Demo heading present
    assert "Demo" not in headings


def test_settings_page__demo_activity_present__delete_it(import_demo_data, live_server, webdriver):
    models.get_settings()
    webdriver.get(live_server.url + reverse("settings"))

    assert webdriver.find_element_by_tag_name("h3").text == "Settings"

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h5")]
    assert "File Importer" in headings
    assert "Reimporter" in headings

    # verify no demo activity is present
    assert len(models.Activity.objects.filter(is_demo_activity=True)) == 19
    # Demo heading is present
    assert "Demo" in headings

    # also delete demo activity button is present
    first_delete_button = webdriver.find_element_by_id("delete-demo-data")
    assert first_delete_button.text == "  Delete"

    # click button to verify demo data gets deleted
    first_delete_button.click()
    assert webdriver.current_url == live_server.url + reverse("delete-demo-data")

    # on the new page find the additional delete button and click it
    second_delete_button = webdriver.find_element_by_class_name("btn-space")
    assert second_delete_button.text == "  Delete"
    second_delete_button.click()

    # verify that all demo data got deleted
    assert len(models.Activity.objects.filter(is_demo_activity=True)) == 0


def test_settings_page__edit_and_submit_form(live_server, webdriver):
    # get settings and check that all values are at their default configuration
    settings = models.get_settings()
    assert settings.path_to_trace_dir == django_settings.TRACKS_DIR
    assert settings.path_to_garmin_device == "/run/user/1000/gvfs/"
    assert settings.delete_files_after_import is False
    assert settings.number_of_days == 30

    # go to settings page
    webdriver.get(live_server.url + reverse("settings"))
    assert webdriver.find_element_by_tag_name("h3").text == "Settings"

    # modify values by inserting into input fields
    trace_dir_input_field = webdriver.find_element_by_css_selector("#id_path_to_trace_dir")
    trace_dir_input_field.clear()
    trace_dir_input_field.send_keys("some/dummy/path")

    garmin_device_input_field = webdriver.find_element_by_css_selector("#id_path_to_garmin_device")
    garmin_device_input_field.clear()
    garmin_device_input_field.send_keys("garmin/dummy/path")

    # got removed, should not be accessible
    with pytest.raises(NoSuchElementException):
        webdriver.find_element_by_css_selector("#id_reimporter_updates_all")

    delete_files_input_field = webdriver.find_element_by_css_selector("#id_delete_files_after_import")
    delete_files_input_field.click()

    # verify that the number of days field is not present nor editable
    with pytest.raises(NoSuchElementException):
        webdriver.find_element_by_css_selector("#id_number_of_days")

    # find button and submit
    button = webdriver.find_element_by_id("button")
    button.click()

    # again get settings and check that the values are the once entered above
    settings = models.get_settings()
    assert settings.path_to_trace_dir == "some/dummy/path"
    assert settings.path_to_garmin_device == "garmin/dummy/path"
    assert settings.delete_files_after_import is True
    # number of days should not be changed
    assert settings.number_of_days == 30

    # this attribute got removed, so verifying that is does no longer exist
    with pytest.raises(AttributeError):
        assert settings.reimporter_updates_all is True
