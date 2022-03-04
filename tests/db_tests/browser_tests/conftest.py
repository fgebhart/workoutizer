import datetime
from pathlib import Path

import pytest
from selenium.webdriver import Firefox, FirefoxOptions

from workoutizer import settings as django_settings


@pytest.fixture
def webdriver():
    options = FirefoxOptions()
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

    def _take(webdriver, name: str = None, path: str = None):
        if name is None:
            name = f"{datetime.datetime.now()}_screenshot.png"
        if not name.endswith(".png"):
            name = f"{name}.png"
        if path is None:
            path = Path(django_settings.BASE_DIR) / "selenium_ide/debugging" / name
        else:
            path = Path(path) / name

        webdriver.save_screenshot(str(path))

    return _take
