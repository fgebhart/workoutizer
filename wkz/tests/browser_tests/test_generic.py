from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import pytest


def test_sidebar(live_server, webdriver):
    def assert_only_selected_link_is_highlighted(red_link_text: str):
        all_links = webdriver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            if link.text == red_link_text:
                assert link.value_of_css_property("color") == "rgb(239, 129, 87)"
            else:
                assert link.value_of_css_property("color") != "rgb(239, 129, 87)"

    webdriver.get(live_server.url + reverse("home"))
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Dashboard"
    assert webdriver.current_url == live_server.url + reverse("home")
    assert_only_selected_link_is_highlighted("DASHBOARD")

    # test element in sidebar
    webdriver.find_element(By.LINK_TEXT, "ADD SPORT").click()
    assert webdriver.current_url == live_server.url + reverse("add-sport")
    assert_only_selected_link_is_highlighted("ADD SPORT")

    webdriver.find_element(By.LINK_TEXT, "AWARDS").click()
    assert webdriver.current_url == live_server.url + reverse("awards")
    assert_only_selected_link_is_highlighted("AWARDS")

    # test clicking on "WORKOUTIZER" in the sidebar
    webdriver.find_element(By.LINK_TEXT, "WORKOUTIZER").click()
    assert webdriver.current_url == live_server.url + reverse("home")
    assert_only_selected_link_is_highlighted("DASHBOARD")

    webdriver.find_element(By.LINK_TEXT, "SPORTS").click()
    assert webdriver.current_url == live_server.url + reverse("sports")
    assert_only_selected_link_is_highlighted("SPORTS")

    # minimize sidebar
    webdriver.find_element(By.CSS_SELECTOR, ".nc-minimal-left").click()

    # verify dumpbell img is present
    webdriver.find_element(By.TAG_NAME, "img").click()
    assert webdriver.current_url == live_server.url + reverse("home")
    assert_only_selected_link_is_highlighted("DASHBOARD")

    # now check that both normal logo (text) and mini logo (img) are visible
    webdriver.find_element(By.CLASS_NAME, "logo-normal")
    webdriver.find_element(By.CLASS_NAME, "logo-mini")

    # again minimize sidebar
    webdriver.find_element(By.CSS_SELECTOR, ".nc-minimal-left").click()
    # maximize
    webdriver.find_element(By.CSS_SELECTOR, ".nc-minimal-right").click()
    assert webdriver.current_url == live_server.url + reverse("home")


def test_responsiveness(live_server, webdriver):
    # first go to dashboard page
    webdriver.get(live_server.url + reverse("home"))
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Dashboard"
    assert webdriver.current_url == live_server.url + reverse("home")

    # check home logo is present and interactable
    webdriver.find_element(By.LINK_TEXT, "WORKOUTIZER").click()

    # also check that navbar items are present
    webdriver.find_element(By.ID, "add-activity-button")
    webdriver.find_element(By.ID, "help-button")
    webdriver.find_element(By.ID, "settings-button")

    # see that navbar toggler is not yet interactable
    with pytest.raises(ElementNotInteractableException):
        webdriver.find_element(By.CLASS_NAME, "navbar-toggler").click()
    # same for navbar kebab
    with pytest.raises(ElementNotInteractableException):
        webdriver.find_element(By.CLASS_NAME, "navbar-kebab").click()

    # now change window size to be small in order to trigger the responsiveness of both the sidebar and navbar
    webdriver.set_window_size(800, 600)
    # wait for the sidebar to be collapsed
    WebDriverWait(webdriver, 3).until(EC.invisibility_of_element_located((By.LINK_TEXT, "WORKOUTIZER")))

    # check that home logo has gone
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.LINK_TEXT, "WORKOUTIZER")
    # same for other sidebar items
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.LINK_TEXT, "SPORTS")
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.LINK_TEXT, "AWARDS")
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.LINK_TEXT, "ADD SPORT")

    # now toggle the sidebar to expand again
    webdriver.find_element(By.CLASS_NAME, "navbar-toggler").click()
    # sidebar items should be present again
    webdriver.find_element(By.LINK_TEXT, "WORKOUTIZER")
    webdriver.find_element(By.LINK_TEXT, "SPORTS")
    webdriver.find_element(By.LINK_TEXT, "AWARDS")
    webdriver.find_element(By.LINK_TEXT, "ADD SPORT")
    # collapse sidebar again (by clicking into body) and wait until it is gone
    webdriver.find_element(By.ID, "bodyClick").click()
    WebDriverWait(webdriver, 3).until(EC.invisibility_of_element_located((By.ID, "bodyClick")))

    # verify navbar kebab is present and interactable
    webdriver.find_element(By.CLASS_NAME, "navbar-kebab")

    # navbar items are currently not visible
    with pytest.raises(ElementNotInteractableException):
        webdriver.find_element(By.ID, "add-activity-button").click()
    with pytest.raises(ElementNotInteractableException):
        webdriver.find_element(By.ID, "help-button").click()
    with pytest.raises(ElementNotInteractableException):
        webdriver.find_element(By.ID, "settings-button").click()

    # click navbar kebab to expand navbar items
    webdriver.find_element(By.CLASS_NAME, "navbar-kebab").click()

    # verify navbar items are visible and interactable again
    webdriver.find_element(By.ID, "add-activity-button").click()
    webdriver.find_element(By.CLASS_NAME, "navbar-kebab").click()
    webdriver.find_element(By.ID, "help-button").click()
    webdriver.find_element(By.CLASS_NAME, "navbar-kebab").click()
    webdriver.find_element(By.ID, "settings-button").click()


def test_custom_navbar_items(live_server, webdriver, import_one_activity, take_screenshot):
    default_slugs = ["add-activity", "settings", "help", "awards", "sports", "add-sport"]
    all_possible_slugs = set(default_slugs + ["edit", "download"])

    def _assert_that_only_these_slugs_are_present(slugs_to_check: list):
        links = [cell.get_attribute("href") for cell in webdriver.find_elements(By.TAG_NAME, "a")]
        present_slugs = []
        for link in links:
            if link:
                link = link.split("/")[
                    -2
                ]  # get second last entry since url looks e.g. 'http://localhost:45063/add-activity/'
                present_slugs.append(link)
        for slug in slugs_to_check:
            assert slug in present_slugs
        # check that the remaining ones are not present
        for slug in all_possible_slugs - set(slugs_to_check):
            assert slug not in present_slugs

    # check that on dashboard page only add-activity, help and settings are present
    webdriver.get(live_server.url + reverse("home"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for awards page
    webdriver.get(live_server.url + reverse("awards"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for sports page
    webdriver.get(live_server.url + reverse("sports"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for add-activity page
    webdriver.get(live_server.url + reverse("sports"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for help page
    webdriver.get(live_server.url + reverse("help"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for settings page
    webdriver.get(live_server.url + reverse("settings"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    # same for add-sport page
    webdriver.get(live_server.url + reverse("add-sport"))
    _assert_that_only_these_slugs_are_present(default_slugs)

    import_one_activity("cycling_bad_schandau.fit")
    # sport page should have default slugs + edit slug
    webdriver.get(live_server.url + "/sport/unknown")
    _assert_that_only_these_slugs_are_present(default_slugs + ["edit"])

    # activity page should have default slugs + edit + download
    webdriver.get(live_server.url + "/activity/1")
    take_screenshot(webdriver, "download")
    _assert_that_only_these_slugs_are_present(default_slugs + ["edit", "download"])
