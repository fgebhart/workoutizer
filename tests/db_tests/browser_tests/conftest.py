import datetime
from pathlib import Path

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from workoutizer import settings as django_settings


@pytest.fixture
def webdriver():
    options = Options()
    options.headless = True
    driver = Firefox(options=options)
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
