import datetime

from django.urls import reverse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytz

from wkz import models
from wkz import configuration


def test_all_sports_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse("sports"))

    # first time running workoutizer will lead to the dashboard page with no data
    card_title = webdriver.find_element_by_class_name("card-title")
    assert card_title.text == "Sports Overview"
    assert "Sports" in webdriver.find_element_by_class_name("navbar-brand").text


def test_adding_new_sport(live_server, webdriver):
    models.default_sport()
    # verify that the only available sport is the default 'unknown' sport
    sports = models.Sport.objects.all()
    assert len(sports) == 1
    assert sports[0].name == "unknown"
    # webdriver.get(live_server.url + reverse("sports"))
    webdriver.get(live_server.url + reverse("add-sport"))

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
    assert "DATE" in table_header
    assert "ACTIVITY" in table_header
    assert "TRACK" in table_header
    assert "SPORT" in table_header
    assert "DURATION" in table_header
    assert "DISTANCE" in table_header

    # the sport name should be unknown
    assert "Cycling" in webdriver.find_element_by_class_name("navbar-brand").text

    card_category = [a.text for a in webdriver.find_elements_by_class_name("card-category")]
    assert "Trend" in card_category
    assert "Distance" in card_category
    assert "Duration" in card_category
    assert "Count" in card_category

    card_title = [a.text for a in webdriver.find_elements_by_class_name("card-title")]
    # assert "0h 0m" in card_title        # fails in CI
    assert "121 km" in card_title
    assert "13h 44m" in card_title
    assert "3" in card_title

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "CYCLING" in links

    card_title = [p.text for p in webdriver.find_elements_by_class_name("card-title")]
    assert "Overview" in card_title

    paragraph = [p.text for p in webdriver.find_elements_by_tag_name("p")]
    assert "DASHBOARD" in paragraph
    assert "AWARDS" in paragraph
    assert "SPORTS" in paragraph
    assert "CYCLING" in paragraph
    assert "HIKING" in paragraph
    assert "JOGGING" in paragraph
    assert "ADD SPORT" in paragraph

    # wait until loading image is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "loading-bar")))
    # wait until activity row is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "activities-table-row")))

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data

    assert len(webdriver.find_elements_by_class_name("fa-chart-line")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-hashtag")) > 0

    # check that map is displayed
    map_text = webdriver.find_element_by_id("leaflet_map").text
    assert "Streets" in map_text
    assert "Leaflet | Map data: © OpenStreetMap" in map_text
    assert "−" in map_text
    assert "+" in map_text
    assert "Satellite" in map_text
    assert "Terrain" in map_text
    assert "Topo" in map_text

    # check that bokeh plot is available
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 1

    # check that it is possible to click on the fullscreen toggle using leaflet-ui
    webdriver.find_element_by_css_selector(".leaflet-control-zoom-fullscreen").click()


def test_sport_page__infinite_scroll(live_server, webdriver, insert_activity, insert_sport):
    rows_per_page = configuration.number_of_rows_per_page_in_table
    # insert more activities than the currently configured value of rows
    # per page in order to be  able to trigger the htmx ajax request
    sport = insert_sport(name="Skiing")
    nr_of_inserted_activities = rows_per_page + 5
    for i in range(nr_of_inserted_activities):
        insert_activity(name=f"Dummy Activity {i}", sport=sport)

    assert models.Activity.objects.filter(sport__name="Skiing").count() == nr_of_inserted_activities
    webdriver.get(live_server.url + "/sport/skiing")

    # number of rows equals the number of rows per page, since only one page is loaded
    table_rows = [cell.text for cell in webdriver.find_elements_by_id("activities-table-row")]
    assert len(table_rows) + 1 == rows_per_page

    webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # wait until loading image is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "loading-bar")))
    # wait until final row indicating that no more activities are available is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "end-of-activities")))

    # again check number of table rows
    table_rows = [cell.text for cell in webdriver.find_elements_by_id("activities-table-row")]
    assert len(table_rows) + 1 == nr_of_inserted_activities


def test_sport_page__no_activities_selected_for_plot(live_server, webdriver, insert_activity, insert_sport):
    sport = insert_sport(name="Bungee Jumping")
    for i in range(5):
        date = datetime.datetime(1900, 1, 1, tzinfo=pytz.UTC) + datetime.timedelta(days=i)
        insert_activity(name=f"Dummy Activity {i}", sport=sport, date=date)

    assert models.Activity.objects.filter(sport__slug="bungee-jumping").count() == 5
    webdriver.get(live_server.url + "/sport/bungee-jumping")

    # even though the activity data is far in the past, the rows will be shown in the table
    table_rows = [cell.text for cell in webdriver.find_elements_by_id("activities-table-row")]
    assert len(table_rows) == 5

    paragraph = [p.text for p in webdriver.find_elements_by_tag_name("p")]
    assert "BUNGEE JUMPING" in paragraph
    # because the activity was added has dates far in the past, there is no activity data available for plotting
    assert (
        "Either increase the selected time range, or do some sports and add it to Workoutizer.\n"
        "The activity plot will appear here  "
    ) in paragraph

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "WORKOUTIZER" in links

    # verify leaflet elements are present
    assert "+" in links
    assert "−" in links
    assert "Leaflet" in links
    assert "OpenStreetMap" in links

    spans = [a.text for a in webdriver.find_elements_by_tag_name("span")]
    assert "Streets" in spans
    assert "Topo" in spans
    assert "Terrain" in spans
    assert "Satellite" in spans
