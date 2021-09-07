import datetime
from pathlib import Path

import pytest
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions

from workoutizer import settings as django_settings


@pytest.fixture(params=["chrome", "firefox"])
def webdriver(request):
    if request.param == "firefox":
        options = FirefoxOptions()
        options.headless = True
        driver = Firefox(options=options)
    if request.param == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")  # This can probally be removed when #30 is fixed
        options.add_argument("--disable-dev-shm-usage")  # https://stackoverflow.com/a/53970825
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
