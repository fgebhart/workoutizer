import pytest
from selenium.webdriver import Firefox


@pytest.yield_fixture(scope="session")
def webdriver():
    driver = Firefox()
    yield driver
    driver.quit()
