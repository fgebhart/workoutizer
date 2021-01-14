from django.urls import reverse


def test_awards_page__complete(import_demo_data, live_server, webdriver):
    webdriver.get(live_server.url + reverse("awards"))

    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "Rank" in table_header
    assert "Fastest" in table_header
    assert "Date" in table_header
    assert "Activity" in table_header
    assert "Speed" in table_header

    assert "Your Awards" in webdriver.find_element_by_tag_name("h3").text

    h4 = [h4.text for h4 in webdriver.find_elements_by_tag_name("h4")]
    assert "Jogging  " in h4
    assert "Hiking  " in h4
    assert "Cycling  " in h4

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
    assert "Noon Jogging in Mirow" in links
    assert "Noon Jogging in Heidelberg" in links
    assert "Evening Hiking in Ringgenberg (BE)" in links
    assert "Noon Hiking in Kornau" in links
    assert "Noon Hiking in Bad Schandau" in links
    assert "Noon Cycling in Hinterzarten" in links
    assert "Noon Cycling in Bad Schandau" in links
    assert "Noon Cycling in Dahn" in links

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Noon Hiking in Bad Schandau" in table_data
    assert "Noon Hiking in Kornau" in table_data
    assert "Noon Hiking in Bad Schandau" in table_data
    assert "Evening Hiking in Ringgenberg (BE)" in table_data
    assert "Noon Jogging in Heidelberg" in table_data
    assert "Noon Jogging in Mirow" in table_data
    assert "10.2 km/h" in table_data
    assert "30 km" in table_data

    assert len(webdriver.find_elements_by_class_name("fa-medal")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
