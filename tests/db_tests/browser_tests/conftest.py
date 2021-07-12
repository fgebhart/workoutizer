import datetime
from pathlib import Path

import pytest
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions

from workoutizer import settings as django_settings


# https://qxf2.com/blog/selenium-cross-browser-cross-platform-pytest/
@pytest.fixture
def webdriver(browser):
    if browser.lower() == "firefox":
        options = FirefoxOptions()
        options.headless = True
        driver = Firefox(options=options)
    if browser.lower() == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")  # This can probally be removed when #30 is fixed
        options.headless = True
        driver = Chrome(options=options)
    driver.set_window_size(1280, 1024)
    yield driver
    driver.quit()


@pytest.fixture
def take_screenshot():
    """
    Helper function which is useful when debugging selenium browser tests.
    """

    def _take(webdriver, name="screenshot"):
        path = Path(django_settings.BASE_DIR) / "selenium_ide/debugging" / Path(f"{datetime.datetime.now()}_{name}.png")
        webdriver.save_screenshot(str(path))

    return _take
