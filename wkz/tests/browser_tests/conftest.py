import datetime
from pathlib import Path

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from workoutizer import settings as django_settings
from wkz.file_importer import run_file_importer
from wkz import api
from wkz import models


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


@pytest.fixture(scope="function", autouse=True)
def reimport_sequentially(monkeypatch):
    def reimport_sequentially(request):
        run_file_importer(models, reimporting=True)
        return True

    monkeypatch.setattr(api, "reimport_activities", reimport_sequentially)
