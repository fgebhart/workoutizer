from django.urls import reverse

from wizer import models


def test_settings_page__no_demo_activity(live_server, webdriver):
    models.get_settings()
    webdriver.get(live_server.url + reverse("settings"))

    assert webdriver.find_element_by_tag_name("h3").text == "Settings"

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h5")]
    assert "File Importer" in headings
    assert "Reimporter" in headings

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


def test_settings_page__form(live_server, webdriver):
    # TODO test form fields and filling out and saving the form
    pass
