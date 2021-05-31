from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pytest

from wkz.views import DashboardView


def test_custom_400_page(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))
    assert webdriver.current_url == live_server.url + reverse("home")

    # show that no alert box is visible
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.CLASS_NAME, "alert-danger")

    # try to open non existing page
    webdriver.get(live_server.url + "/does-not-exist")

    # verify that we got redirected to home
    assert webdriver.current_url == live_server.url + reverse("home")

    # verify that the alert box is visible
    webdriver.find_element(By.CLASS_NAME, "alert-danger")


def test_custom_500_page(live_server, webdriver, monkeypatch):
    # mock the DashboardView.get method to provoke a 500 error, get() should return a rendered html, not a string
    def faulty_get_func(self, request):
        return "dummy-string"

    monkeypatch.setattr(DashboardView, "get", faulty_get_func)

    webdriver.get(live_server.url + reverse("home"))
    assert webdriver.current_url == live_server.url + reverse("home")

    # verify that the alert box is visible
    assert "Error while loading" in webdriver.find_element(By.CLASS_NAME, "alert-danger").text

    # verify the correct title of the card
    assert webdriver.find_element(By.CLASS_NAME, "card-title").text == "Error 🤕"
