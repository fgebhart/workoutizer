import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from wizer import models


def test_activity_page__complete(import_one_activity, live_server, webdriver):
    import_one_activity("2020-08-29-13-04-37.fit")

    pk = models.Activity.objects.get().pk
    webdriver.get(live_server.url + f"/activity/{pk}")

    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "  Duration:  4:59 h" in table_header
    assert "  Distance:  44.96 km" in table_header
    assert "  Calories:  1044 kcal" in table_header
    assert "Time" in table_header
    assert "Distance" in table_header
    assert "Pace" in table_header
    assert "Label" in table_header

    assert webdriver.find_element_by_tag_name("h3").text == "Noon Cycling in Bad Schandau  "

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h5")]
    assert "Fastest Sections  " in headings
    assert "Speed" in headings
    assert "Pace" in headings
    assert "Temperature" in headings
    assert "Laps" in headings

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
    assert "+" in links
    assert "−" in links
    assert "Leaflet" in links
    assert "OpenStreetMap" in links
    ps = [p.text for p in webdriver.find_elements_by_tag_name("p")]
    assert "Aug 29, 2020, 17:12" in ps

    # check that icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-fire")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0

    # check that map is displayed
    assert (
        webdriver.find_element_by_id("map").text
        == "Streets\nTopo\nTerrain\nSatellite\n+\n−\n2 km\nLeaflet | Map data: © OpenStreetMap"
    )

    # check that bokeh plots are available
    assert webdriver.find_element_by_class_name("bk-root").text == "Show Laps"
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 3


def test_edit_activity_page(import_one_activity, live_server, webdriver):
    import_one_activity("2020-08-29-13-04-37.fit")

    activity = models.Activity.objects.get()
    pk = activity.pk
    webdriver.get(live_server.url + f"/activity/{pk}")
    # verify that activity has some awards
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0

    webdriver.get(live_server.url + f"/activity/{pk}/edit")

    assert activity.name == "Noon Cycling in Bad Schandau"
    assert activity.duration == datetime.timedelta(seconds=17970)
    assert activity.is_demo_activity is False
    assert activity.evaluates_for_awards is True
    # make activity a demo activity to verify it won't get changed back
    activity.is_demo_activity = True
    activity.save()
    assert activity.is_demo_activity is True

    assert webdriver.find_element_by_tag_name("h3").text == "Edit Activity: Noon Cycling in Bad Schandau (unknown)"
    assert webdriver.find_element_by_tag_name("button").text == "  Save"
    assert (
        webdriver.find_element_by_tag_name("form").text
        == "Activity Name:\nSport:\nunknown\nDate:\nDuration:\n  min\nDistance:\n  km\nDescription:\nConsider this "
        "Activity for Awards:\n  \nLap Data\n\n\n  Save\nCancel\n  Delete"
    )

    links = [link.text for link in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
    assert "Lap Data" in links
    assert "Cancel" in links
    assert "  Delete" in links

    # uncheck the box for evaluates_for_awards
    webdriver.find_element_by_id("id_evaluates_for_awards").click()

    # enter a different name
    name_field = webdriver.find_element_by_css_selector("#id_name")
    name_field.clear()
    name_field.send_keys("Dummy Activity Name")

    # change duration
    duration_field = webdriver.find_element_by_css_selector("#id_duration")
    duration_field.clear()
    duration_field.send_keys("01:11:11")

    # submit form with modified data
    button = webdriver.find_element_by_id("button")
    button.click()

    # verify url got changed to activity view
    assert webdriver.current_url == f"{live_server.url}/activity/{pk}"

    # check that all trophies got removed, since activity no longer evaluates for awards
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 0

    # verify attributes got changed
    activity = models.Activity.objects.get()
    assert activity.name == "Dummy Activity Name"
    assert activity.duration == datetime.timedelta(seconds=4271)
    assert activity.is_demo_activity is True
    assert activity.evaluates_for_awards is False


def test_edit_activity_selenium_ide(insert_activity, webdriver, live_server):
    insert_activity(name="test")
    assert models.Activity.objects.count() == 1

    # enlarge selected time window
    settings = models.get_settings()
    settings.number_of_days = 9999
    settings.save()

    webdriver.get(live_server.url)
    webdriver.find_element(By.LINK_TEXT, "test").click()
    webdriver.find_element(By.ID, "edit-activity").click()
    webdriver.find_element(By.ID, "id_name").click()
    webdriver.find_element(By.ID, "id_name").click()
    webdriver.find_element(By.ID, "id_name").clear()
    webdriver.find_element(By.ID, "id_name").send_keys("renamed name")
    dropdown = webdriver.find_element(By.ID, "id_sport")
    dropdown.find_element(By.XPATH, "//option[. = 'Cycling']").click()
    webdriver.find_element(By.ID, "id_date").click()
    webdriver.find_element(By.CSS_SELECTOR, "tr:nth-child(4) > .day:nth-child(5)").click()
    webdriver.find_element(By.CSS_SELECTOR, "tr:nth-child(3) > .day:nth-child(3)").click()
    webdriver.find_element(By.CSS_SELECTOR, ".glyphicon-time").click()
    webdriver.find_element(By.CSS_SELECTOR, "td:nth-child(3) .glyphicon-chevron-down").click()
    webdriver.find_element(By.CSS_SELECTOR, ".glyphicon-remove").click()
    webdriver.find_element(By.ID, "id_duration").click()
    webdriver.find_element(By.ID, "id_duration").clear()
    webdriver.find_element(By.ID, "id_duration").send_keys("00:31:00")
    webdriver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(6) > .col-sm-9").click()
    webdriver.find_element(By.ID, "id_distance").click()
    webdriver.find_element(By.ID, "id_distance").send_keys("2.0")
    webdriver.find_element(By.ID, "id_description").click()
    webdriver.find_element(By.ID, "id_description").send_keys("asdf")
    webdriver.find_element(By.ID, "submit-button").submit()

    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert")))
    assert webdriver.current_url == live_server.url + "/activity/1"
    webdriver.save_screenshot(f"selenium_ide/debugging/{datetime.datetime.now()}_edit_activity.png")

    assert "Successfully modified 'renamed name'" in webdriver.find_element(By.CSS_SELECTOR, ".alert").text
