import datetime

from selenium.webdriver.common.by import By
from django.urls import reverse

from workoutizer.__init__ import __version__


def test_help_page(live_server, webdriver):
    webdriver.get(live_server.url + reverse("help"))
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Help"

    card_title = [a.text for a in webdriver.find_elements_by_class_name("card-title")]

    # check version card
    assert "Version" in card_title
    assert webdriver.find_element(By.CLASS_NAME, "badge").text == __version__

    # check source code card
    hrefs = [a.get_attribute("href") for a in webdriver.find_elements_by_tag_name("a")]
    assert "Source Code" in card_title
    assert "https://github.com/fgebhart/workoutizer" in hrefs

    # check keyboard navigation card
    assert "Keyboard Navigation" in card_title
    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Go to Dashboard" in table_data
    assert "g + d" in table_data

    assert "Go to all Sports" in table_data
    assert "g + s" in table_data

    assert "Go to Awards" in table_data
    assert "g + a" in table_data

    assert "Go to Sport" in table_data
    assert "g + Number" in table_data

    assert "Go to edit Sport/Activity" in table_data
    assert "g + e" in table_data

    assert "Go to Settings" in table_data
    assert "g + ," in table_data

    assert "Go to Help" in table_data
    assert "g + h" in table_data

    assert "Go to add Activity" in table_data
    assert "g + n" in table_data

    assert "Toggle Sidebar" in table_data
    assert "[" in table_data

    # check that "made with love" text is present
    assert (
        f"© {datetime.datetime.now().date().year}, made with by Fabian Gebhart"
        in webdriver.find_element(By.CLASS_NAME, "credits").text
    )
