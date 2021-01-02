from django.urls import reverse
from wizer import models


def test_all_sports_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse("sports"))

    # first time running workoutizer will lead to the dashboard page with no data
    h3 = webdriver.find_element_by_css_selector("h3")
    assert h3.text == "Your Sports"


def test_adding_new_sport(live_server, webdriver):
    models.default_sport()
    # verify that the only available sport is the default 'unknown' sport
    sports = models.Sport.objects.all()
    assert len(sports) == 1
    assert sports[0].name == "unknown"
    webdriver.get(live_server.url + reverse("sports"))

    # ensure button to add new sport actually redirects to add sport page
    webdriver.find_element_by_css_selector('a[href="/add-sport/"]').click()
    assert webdriver.current_url == live_server.url + reverse("add-sport")

    # fill out form to add new sport
    sport_name_input_field = webdriver.find_element_by_css_selector("#id_name")
    sport_name_input_field.clear()
    sport_name_input_field.send_keys("UltimateFrisbee")

    icon_input_field = webdriver.find_element_by_css_selector("#id_icon")
    icon_input_field.clear()
    icon_input_field.send_keys("compact-disc")

    # TODO: color seems not to work that way, will leave it for now...
    color_input_field = webdriver.find_element_by_css_selector("#id_color")
    color_input_field.clear()
    color_input_field.send_keys("#FF1F3D")

    # find button and submit
    button = webdriver.find_element_by_id("button")
    button.click()

    # check that a new sport was added
    sports = models.Sport.objects.all()
    assert len(sports) == 2

    new_sport = models.Sport.objects.get(name="UltimateFrisbee")
    assert new_sport.icon == "compact-disc"
    # TODO check why color can not be changed that way
    # assert new_sport.color == "#FF1F3D"


def test_sport_page__complete(import_demo_data, live_server, webdriver):
    # import demo activity and check that all expected elements are available on the sport page
    webdriver.get(live_server.url + "/sport/cycling")

    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "Date" in table_header
    assert "Activity" in table_header
    assert "Track" in table_header
    assert "Sport" in table_header
    assert "Duration" in table_header
    assert "Distance" in table_header

    # the sport name should be unknown
    assert "Cycling" in webdriver.find_element_by_tag_name("h3").text

    assert "Summary" in webdriver.find_element_by_tag_name("h5").text

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
    assert "  Edit Sport" in links

    paragraph = [p.text for p in webdriver.find_elements_by_tag_name("p")]
    assert "Overview of your Cycling activities:" in paragraph
    assert "Map of selected Cycling activities:" in paragraph
    assert "Sum of all selected Activities:" in paragraph

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Noon Cycling in Dahn" in table_data

    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0

    # check that map is displayed
    assert (
        webdriver.find_element_by_id("map").text
        == "Streets\nTopo\nTerrain\nSatellite\n+\n−\n100 km\nLeaflet | Map data: © OpenStreetMap"
    )

    # check that bokeh plot is available
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 1

    # check that it is possible to click on the fullscreen toggle using leaflet-ui
    webdriver.find_element_by_css_selector(".leaflet-control-zoom-fullscreen").click()
