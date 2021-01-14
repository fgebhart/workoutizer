from wizer import models


def test_activity_page__complete(import_one_activity, live_server, webdriver):
    import_one_activity("2020-08-29-13-04-37.fit")

    pk = models.Activity.objects.get().pk
    webdriver.get(live_server.url + f"/activity/{pk}")

    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "  Duration:  4:59 h" in table_header
    assert "  Distance:  44.96 km" in table_header
    assert "  Calories:  1044 kcal" in table_header
    assert "Time" in table_header
    assert "Distance" in table_header
    assert "Pace" in table_header
    assert "Label" in table_header

    assert webdriver.find_element_by_tag_name("h3").text == "Noon Cycling in Bad Schandau  "

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h5")]
    assert "Fastest Sections" in headings
    assert "Speed" in headings
    assert "Pace" in headings
    assert "Temperature" in headings
    assert "Laps" in headings

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
    assert "+" in links
    assert "−" in links
    assert "Leaflet" in links
    assert "OpenStreetMap" in links
    assert webdriver.find_element_by_tag_name("p").text == "Aug 29, 2020, 17:12"

    # check that icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-fire")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0

    # check that map is displayed
    assert (
        webdriver.find_element_by_id("map").text
        == "Streets\nTopo\nTerrain\nSatellite\n+\n−\n2 km\nLeaflet | Map data: © OpenStreetMap"
    )

    # check that bokeh plots are available
    assert webdriver.find_element_by_class_name("bk-root").text == "Show Laps"
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 3
