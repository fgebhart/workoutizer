import time

from django.urls import reverse

delay = 1


def test_dashboard_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse('home'))

    time.sleep(delay)

    # first time running workoutizer will lead to the dashboard page with no data
    h3 = webdriver.find_element_by_css_selector('h3')
    assert h3.text == "no Activity data found"


def test_add_activity_button(live_server, webdriver):
    webdriver.get(live_server.url + reverse('home'))

    time.sleep(delay)

    # ensure button to create new data is actually redirecting to add activity page
    webdriver.find_element_by_tag_name('a').click()
    assert webdriver.current_url == live_server.url + reverse('add-activity')


def test_nav_bar_items(live_server, webdriver):
    webdriver.get(live_server.url + reverse('home'))

    time.sleep(delay)

    # ensure nav bar link to settings page works
    webdriver.find_element_by_css_selector('a[data-original-title="Settings"]').click()
    assert webdriver.current_url == live_server.url + reverse('settings')

    # ensure nav bar link to help page works
    webdriver.find_element_by_css_selector('a[data-original-title="Help"]').click()
    assert webdriver.current_url == live_server.url + reverse('help')
