import time

from django.urls import reverse

delay = 1


def test_all_sports_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse('sports'))

    time.sleep(delay)

    # first time running workoutizer will lead to the dashboard page with no data
    h3 = webdriver.find_element_by_css_selector('h3')
    assert h3.text == "Your Sports"


def test_add_new_sport_button(live_server, webdriver):
    webdriver.get(live_server.url + reverse('sports'))

    time.sleep(delay)

    # ensure button to add new sport actually redirects to add sport page
    webdriver.find_element_by_css_selector('a[href="/add-sport/"]').click()
    assert webdriver.current_url == live_server.url + reverse('add-sport')
