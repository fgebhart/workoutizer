import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options


@pytest.yield_fixture(scope="session")
def webdriver():
    options = Options()
    options.headless = True
    driver = Firefox(options=options)
    yield driver
    driver.quit()
