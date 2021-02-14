from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException
import pytest


def test_dashboard_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # first time running workoutizer will lead to the dashboard page with no data
    h3 = webdriver.find_element_by_css_selector("h3")
    assert h3.text == "No activity data found."


def test_add_activity_button(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # ensure button to create new data is actually redirecting to add activity page
    webdriver.find_element_by_tag_name("a").click()
    assert webdriver.current_url == live_server.url + reverse("add-activity")


def test_nav_bar_items(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # ensure nav bar link to settings page works
    webdriver.find_element_by_id("settings-link").click()
    assert webdriver.current_url == live_server.url + reverse("settings")

    # ensure nav bar link to help page works
    webdriver.find_element_by_id("help-link").click()
    assert webdriver.current_url == live_server.url + reverse("help")


def test_drop_down_visible(live_server, webdriver, settings):
    webdriver.get(live_server.url + reverse("home"))
    days = settings.number_of_days

    dropdown_button = webdriver.find_element_by_id("dropdown-btn")
    assert dropdown_button.text == str(days)


def test_dashboard_page__complete(import_demo_data, live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # verify pie-chart is present
    pie_chart = webdriver.find_element(By.CLASS_NAME, "fa-chart-pie")

    # but cannot be clicked
    with pytest.raises(ElementNotInteractableException):
        pie_chart.click()

    # when zooming in a lot the pie chart actually becomes interactable
    webdriver.set_window_size(800, 600)
    # clicking will not raise an error and will slide right sidebar into screen
    pie_chart.click()

    # clicking into screen again will make the right sidebar disappear
    webdriver.find_element(By.CSS_SELECTOR, ".col-sm-9").click()

    # check that all activity names are in the table
    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Jogging in Heidelberg" in table_data
    assert "Swimming" in table_data
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Evening Hiking in Ringgenberg (BE)" in table_data
    assert "Noon Hiking in Kornau" in table_data

    # check that the trophy icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0

    # check that sport icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-bicycle")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-hiking")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-running")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-swimmer")) > 0

    # check left side bar icons are present
    assert len(webdriver.find_elements_by_class_name("fa-chart-line")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-medal")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-list")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-plus")) == 2

    # check icons in top navbar are present
    assert len(webdriver.find_elements_by_class_name("fa-list")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-dumbbell")) == 2
    assert len(webdriver.find_elements_by_class_name("fa-cogs")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-question-circle")) == 1

    # check icons in right sidebar are present
    assert len(webdriver.find_elements_by_class_name("fa-hashtag")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-road")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-history")) == 1
