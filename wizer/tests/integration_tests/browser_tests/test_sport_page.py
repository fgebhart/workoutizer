import datetime

from django.urls import reverse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytz

from wizer import models
from wizer import configuration


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

    # wait until loading image is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "loading-bar")))
    # wait until activity row is present
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.ID, "activities-table-row")))

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data

    centered = [cell.text for cell in webdriver.find_elements_by_tag_name("center")]
    assert "Sum of all Activities:" in centered

    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0

    # check that map is displayed
    map_text = webdriver.find_element_by_id("map").text
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
    assert "Overview of your Bungee Jumping activities:" in paragraph
    # because the activity was added has dates far in the past, there is no activity data available for plotting
    assert (
        "Either increase the selected time range, or do some sports and add it to Workoutizer.\n"
        "The activity plot will appear here  "
    ) in paragraph

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
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
