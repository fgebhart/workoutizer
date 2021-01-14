from django.urls import reverse


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
    webdriver.find_element_by_css_selector('a[data-original-title="Settings"]').click()
    assert webdriver.current_url == live_server.url + reverse("settings")

    # ensure nav bar link to help page works
    webdriver.find_element_by_css_selector('a[data-original-title="Help"]').click()
    assert webdriver.current_url == live_server.url + reverse("help")


def test_drop_down_visible(live_server, webdriver, settings):
    webdriver.get(live_server.url + reverse("home"))
    days = settings.number_of_days

    dropdown_button = webdriver.find_element_by_id("dropdown-btn")
    assert dropdown_button.text == str(days)


def test_dashboard_page__complete(import_demo_data, live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))
    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]

    # check that all activity names are in the table
    assert "Noon Jogging in Heidelberg" in table_data
    assert "Swimming" in table_data
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Evening Hiking in Ringgenberg (BE)" in table_data
    assert "Noon Hiking in Kornau" in table_data

    # check that the trophy icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
