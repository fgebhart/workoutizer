import datetime

import pytest
import pytz
from django.urls import reverse
from django.utils import timezone
from PIL import Image, ImageColor
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from wkz import models
from wkz.tools.style import Colors


def test_activity_page__complete__fit(import_one_activity, live_server, webdriver):
    import_one_activity("cycling_bad_schandau.fit")

    activity = models.Activity.objects.get()
    pk = activity.pk
    webdriver.get(live_server.url + f"/activity/{pk}")

    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "#" in table_header
    assert "TIME" in table_header
    assert "DISTANCE" in table_header
    assert "PACE" in table_header
    assert "TRIGGER" in table_header
    assert "LABEL" in table_header

    # check summary facts
    card_category = [cell.text for cell in webdriver.find_elements_by_class_name("card-category")]
    assert "Date" in card_category
    assert "Distance" in card_category
    assert "Duration" in card_category
    assert "Calories" in card_category
    card_title = [cell.text for cell in webdriver.find_elements_by_class_name("card-title")]
    assert "4h 59m" in card_title
    assert "44.96 km" in card_title
    assert "1044 kcal" in card_title
    assert "29. Aug 20" in card_title

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    # best sections
    assert "  1km" in table_data
    assert "  2km" in table_data
    assert "  3km" in table_data
    assert "  5km" in table_data
    assert "  10km" in table_data
    assert "29.7 km/h" in table_data
    assert "25.0 km/h" in table_data

    # avg + min + max values
    assert "max" in table_data
    assert "high" in table_data
    assert "avg" in table_data
    assert "min" in table_data
    assert "9.0 km/h" in table_data
    assert "47.9 km/h" in table_data
    assert "06:39 min/km" in table_data
    assert "01:15 min/km" in table_data
    assert "23.0 °C" in table_data
    assert "26.0 °C" in table_data
    assert "32.0 °C" in table_data
    assert "1" in table_data
    assert "1:46:15" in table_data
    assert "11423" in table_data
    assert "09:18" in table_data
    assert "447 m" in table_data  # total ascent
    assert "451 m" in table_data  # total descent

    # check that lap triggers are in lap table
    assert "manual" in table_data
    assert "session_end" in table_data

    assert webdriver.find_element_by_class_name("navbar-brand").text == "Noon Cycling In Bad Schandau"

    # check card titles
    assert "Fastest Sections  " in card_title
    assert "Best Climb Sections  " in card_title
    assert "Speed" in card_title
    assert "Pace" in card_title
    assert "Temperature" in card_title
    assert "Laps" in card_title
    assert "Elevation" in card_title

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "WORKOUTIZER" in links
    assert "DASHBOARD" in links
    assert "AWARDS" in links
    assert "SPORTS" in links
    assert "ADD SPORT" in links
    assert "+" in links
    assert "−" in links
    assert "Leaflet" in links
    assert "OpenStreetMap" in links

    spans = [a.text for a in webdriver.find_elements_by_tag_name("span")]
    assert "Streets" in spans
    assert "Topo" in spans
    assert "Terrain" in spans
    assert "Satellite" in spans

    # check that icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-fire")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-calendar-alt")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-arrow-down")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-arrow-up")) > 0

    # check that map is displayed
    assert (
        webdriver.find_element_by_id("leaflet_map").text
        == "Streets\nTopo\nTerrain\nSatellite\n+\n−\n3 km\nLeaflet | Map data: © OpenStreetMap"
    )

    # check that bokeh plots are available
    assert webdriver.find_element_by_class_name("bk-root").text == "Show Auto Laps\nShow Manual Laps"
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 3

    # check that streets is the default map layer
    default_layer = [
        span.text
        for span in webdriver.find_elements_by_css_selector(
            ".leaflet-control-layers-inline .leaflet-control-layers-base input:checked+span"
        )
    ]
    assert len(default_layer) == 1
    assert "Streets" in default_layer


def test_activity_page__complete__gpx(import_one_activity, live_server, webdriver):
    import_one_activity("cycling_walchensee.gpx")

    activity = models.Activity.objects.get()
    pk = activity.pk
    webdriver.get(live_server.url + f"/activity/{pk}")

    # check summary facts
    card_category = [cell.text for cell in webdriver.find_elements_by_class_name("card-category")]
    assert "Date" in card_category
    assert "Distance" in card_category
    assert "Duration" in card_category
    assert "Calories" in card_category
    card_title = [cell.text for cell in webdriver.find_elements_by_class_name("card-title")]
    assert "3h 32m" in card_title
    assert "82.6 km" in card_title
    assert "- kcal" in card_title
    assert "28. May 21" in card_title

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    # best sections
    assert "  1km" in table_data
    assert "  2km" in table_data
    assert "  3km" in table_data
    assert "  5km" in table_data
    assert "  10km" in table_data
    assert "51.3 km/h" in table_data
    assert "49.9 km/h" in table_data

    assert webdriver.find_element_by_class_name("navbar-brand").text == "Early Morning Cycling In Kochel Am See"

    # check card titles
    assert "Fastest Sections  " in card_title
    assert "Best Climb Sections  " in card_title

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "WORKOUTIZER" in links
    assert "DASHBOARD" in links
    assert "AWARDS" in links
    assert "SPORTS" in links
    assert "ADD SPORT" in links
    assert "+" in links
    assert "−" in links
    assert "Leaflet" in links
    assert "OpenStreetMap" in links

    spans = [a.text for a in webdriver.find_elements_by_tag_name("span")]
    assert "Streets" in spans
    assert "Topo" in spans
    assert "Terrain" in spans
    assert "Satellite" in spans

    # check that icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-fire")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-road")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-history")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-calendar-alt")) > 0

    # check that map is displayed
    assert (
        webdriver.find_element_by_id("leaflet_map").text
        == "Streets\nTopo\nTerrain\nSatellite\n+\n−\n10 km\nLeaflet | Map data: © OpenStreetMap"
    )

    # check that only one bokeh plot is available
    assert len(webdriver.find_elements_by_class_name("bk-canvas")) == 1

    # check that streets is the default map layer
    default_layer = [
        span.text
        for span in webdriver.find_elements_by_css_selector(
            ".leaflet-control-layers-inline .leaflet-control-layers-base input:checked+span"
        )
    ]
    assert len(default_layer) == 1
    assert "Streets" in default_layer


def test_edit_activity_page(import_one_activity, live_server, webdriver, insert_sport):
    # add some sports
    insert_sport("Cycling")
    insert_sport("MTB")
    assert models.Sport.objects.count() == 2

    # activity will be mapped to sport "Cycling"
    import_one_activity("cycling_bad_schandau.fit")

    activity = models.Activity.objects.get()
    pk = activity.pk
    assert activity.sport.name == "Cycling"

    # save initial date
    initial_date = activity.date

    webdriver.get(live_server.url + f"/activity/{pk}")

    # verify that activity has some awards
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    # because it currently evaluates for awards there is no exclamation circle icon
    assert len(webdriver.find_elements_by_class_name("fa-exclamation-circle")) == 0

    # go to edit activity page by clicking the edit button
    button = webdriver.find_element_by_id("edit-activity-button")
    button.click()

    # verify url got changed to activity view
    assert webdriver.current_url == f"{live_server.url}/activity/{pk}/edit/"

    assert activity.name == "Noon Cycling in Bad Schandau"
    assert activity.duration == datetime.timedelta(seconds=17970)
    assert activity.is_demo_activity is False
    assert activity.evaluates_for_awards is True
    # make activity a demo activity to verify it won't get changed back
    activity.is_demo_activity = True
    activity.save()
    assert activity.is_demo_activity is True

    assert webdriver.find_element_by_class_name("navbar-brand").text == "Edit Activity: Noon Cycling In Bad Schandau"
    assert webdriver.find_element_by_id("submit-button").text == "  SAVE"
    form_text = webdriver.find_element_by_tag_name("form").text
    assert "Activity Name" in form_text
    assert "Sport" in form_text
    assert "Cycling" in form_text
    assert "MTB" in form_text
    assert "Date" in form_text
    assert "Duration [HH:MM:SS]" in form_text
    assert "Distance [in km]" in form_text
    assert "Description" in form_text
    assert "Consider Activity for Awards" in form_text
    assert "Lap Data" in form_text
    assert "SAVE" in form_text
    assert "CANCEL" in form_text
    assert "DELETE" in form_text

    links = [link.text for link in webdriver.find_elements_by_tag_name("a")]
    assert "DASHBOARD" in links
    assert "ADD SPORT" in links
    assert "SPORTS" in links
    assert "AWARDS" in links
    assert "WORKOUTIZER" in links
    assert "Lap Data" in links  # means activity has some laps
    assert "CANCEL" in links
    assert "  DELETE" in links
    assert "REPORT AN ISSUE" in links
    assert "" in links

    # uncheck the box for evaluates_for_awards
    webdriver.find_element_by_class_name("form-check-label").click()

    # enter a different name
    name_field = webdriver.find_element_by_css_selector("#id_name")
    name_field.clear()
    name_field.send_keys("Dummy Activity Name")

    # change duration
    duration_field = webdriver.find_element_by_css_selector("#id_duration")
    duration_field.clear()
    duration_field.send_keys("01:11:11")

    # change sport to verify dropdown also works
    dropdown = webdriver.find_element(By.ID, "id_sport")
    dropdown.find_element(By.XPATH, "//option[. = 'MTB']").click()

    # modify the date of the activity to verify the datetime picker widget works
    webdriver.find_element(By.ID, "id_date").click()
    webdriver.find_element(By.CSS_SELECTOR, "tr:nth-child(4) > .day:nth-child(5)").click()
    webdriver.find_element(By.CSS_SELECTOR, "tr:nth-child(3) > .day:nth-child(3)").click()
    webdriver.find_element(By.CSS_SELECTOR, ".fa-clock-o").click()
    WebDriverWait(webdriver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-child(3) .fa-chevron-down")))
    webdriver.find_element(By.CSS_SELECTOR, "td:nth-child(3) .fa-chevron-down").click()

    # also edit lap data
    webdriver.find_element(By.ID, "edit-lap-data").click()
    lap_input_0 = webdriver.find_element(By.ID, "id_form-0-label")
    WebDriverWait(webdriver, 3).until(EC.element_to_be_clickable((By.ID, "id_form-0-label")))
    lap_input_0.clear()
    lap_input_0.send_keys("lap label 0")

    # verify that there is no second element available
    with pytest.raises(NoSuchElementException, match=r'Message: Unable to locate element: |[id="id_form\-1-label"]'):
        webdriver.find_element(By.ID, "id_form-1-label")

    # submit form with modified data
    button = webdriver.find_element_by_id("submit-button")
    button.click()

    # verify url got changed to activity view
    assert webdriver.current_url == f"{live_server.url}/activity/{pk}"

    # check that all trophies got removed, since activity no longer evaluates for awards
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 0
    # two warning exclamation circles are present, one for fastest, one for climb
    assert len(webdriver.find_elements_by_class_name("fa-exclamation-circle")) == 2

    # verify attributes got changed
    activity = models.Activity.objects.get()
    assert activity.name == "Dummy Activity Name"
    assert activity.duration == datetime.timedelta(seconds=4271)
    assert activity.is_demo_activity is True
    assert activity.evaluates_for_awards is False
    assert activity.sport.name == "MTB"
    assert activity.date != initial_date

    # verify that lap label got changed
    laps = models.Lap.objects.filter(trace=activity.trace_file, trigger="manual")
    assert laps[0].label == "lap label 0"


def test_add_activity_page(insert_sport, webdriver, live_server):
    # insert some sports
    insert_sport("Cycling")
    insert_sport("MTB")
    assert models.Sport.objects.count() == 2

    webdriver.get(live_server.url)
    webdriver.find_element(By.ID, "add-activity-button").click()
    assert webdriver.current_url == live_server.url + reverse("add-activity")

    # set name
    WebDriverWait(webdriver, 3).until(EC.element_to_be_clickable((By.ID, "id_name")))
    webdriver.find_element(By.ID, "id_name").click()
    webdriver.find_element(By.ID, "id_name").clear()
    webdriver.find_element(By.ID, "id_name").send_keys("Dummy Activity")
    webdriver.find_element(By.CSS_SELECTOR, "form").click()
    # set sport
    dropdown = webdriver.find_element(By.ID, "id_sport")
    dropdown.find_element(By.XPATH, "//option[. = 'Cycling']").click()
    # set date
    webdriver.find_element(By.ID, "id_date").click()
    webdriver.find_element(By.CSS_SELECTOR, ".fa-clock-o").click()
    # change hours
    WebDriverWait(webdriver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-child(1) .fa-chevron-up")))
    webdriver.find_element(By.CSS_SELECTOR, "td:nth-child(1) .fa-chevron-up").click()
    # change minutes
    webdriver.find_element(By.CSS_SELECTOR, "td:nth-child(3) .fa-chevron-down").click()
    # set duration
    webdriver.find_element(By.ID, "id_duration").clear()
    webdriver.find_element(By.ID, "id_duration").send_keys("00:31:00")
    # set distance
    webdriver.find_element(By.ID, "id_distance").send_keys("2.3")
    # set description
    webdriver.find_element(By.ID, "id_description").send_keys("super sport")
    webdriver.find_element(By.CSS_SELECTOR, "form").click()
    # submit and wait
    webdriver.find_element(By.ID, "submit-button").click()
    WebDriverWait(webdriver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert")))

    assert webdriver.current_url == live_server.url + reverse("home")
    assert "Successfully added 'Dummy Activity'" in webdriver.find_element(By.CSS_SELECTOR, ".alert").text

    assert models.Activity.objects.count() == 1
    activity = models.Activity.objects.get()
    assert activity.name == "Dummy Activity"
    assert activity.duration == datetime.timedelta(minutes=31)
    assert activity.distance == 2.3
    assert activity.description == "super sport"
    assert activity.sport.name == "Cycling"
    assert activity.date.date() == timezone.now().date()


def test_activity_page__rendering_of_sport_icon_on_map(insert_sport, import_one_activity, live_server, webdriver):
    # Test to fix issue GH72
    icon_name = "running"
    insert_sport(name="Jogging", icon=icon_name)

    import_one_activity("2019-09-18-16-02-35.fit")
    activity = models.Activity.objects.get()
    pk = activity.pk

    # check out laps of activity
    assert models.Lap.objects.count() == 2
    laps = models.Lap.objects.all()
    for lap in laps:
        # each lap has at least one coordinate
        assert lap.end_lat is not None or lap.start_lat is not None
        assert lap.end_long is not None or lap.start_long is not None
        assert lap.trigger != "manual"

    # insert an additional lap without any coordinate data
    lap_obj = models.Lap(
        start_time=activity.date,
        end_time=activity.date + datetime.timedelta(minutes=1),
        elapsed_time=-datetime.timedelta(minutes=100),
        trigger="manual",
        start_lat=None,
        start_long=None,
        end_lat=None,
        end_long=None,
        distance=1.0,
        speed=10.0,
        trace=activity.trace_file,
    )
    lap_obj.save()
    assert models.Lap.objects.count() == 3
    new_lap = models.Lap.objects.get(trigger="manual")
    assert new_lap.start_lat is None
    assert new_lap.start_long is None
    assert new_lap.end_lat is None
    assert new_lap.end_long is None

    webdriver.get(live_server.url + f"/activity/{pk}")
    assert webdriver.current_url == f"{live_server.url}/activity/{pk}"

    initial_number_of_sport_icons = len(webdriver.find_elements_by_class_name(f"fa-{icon_name}"))

    headings = [h.text for h in webdriver.find_elements_by_tag_name("h4")]
    assert "Fastest Sections  " in headings
    assert "Best Climb Sections  " in headings
    assert "Cadence" in headings
    assert "Speed" in headings
    assert "Pace" in headings
    assert "Temperature" in headings
    assert "Laps" in headings

    # hover over ploy in order to trigger the rendering of the sport icon on the leaflet map
    altitude_plot = webdriver.find_element(By.CSS_SELECTOR, ".bk:nth-child(1) > .bk > .bk-canvas-events")
    altitude_plot.click()
    hover = ActionChains(webdriver).move_to_element(altitude_plot)
    hover.perform()

    # once sport icon gets rendered we should find one more sport icons than before
    number_of_sport_icons_when_hovering = len(webdriver.find_elements_by_class_name(f"fa-{icon_name}"))
    assert number_of_sport_icons_when_hovering == initial_number_of_sport_icons + 1


def test_activity_page__missing_attributes(import_one_activity, live_server, webdriver):
    import_one_activity("cycling_bad_schandau.fit")

    activity = models.Activity.objects.get()

    # set some attributes to None
    activity.trace_file.avg_speed = None
    activity.trace_file.max_speed = None
    activity.trace_file.max_avg_cadence = None
    activity.trace_file.aerobic_training_effect = None
    activity.trace_file.avg_heart_rate = None
    activity.trace_file.min_temperature = None
    activity.trace_file.save()

    pk = activity.pk
    webdriver.get(live_server.url + f"/activity/{pk}")

    # verify that page load does not fail (without safety measures in place this would fail with TypeError, see GH95)
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Noon Cycling In Bad Schandau"

    # also verify that the sections with missing data are not displayed
    headings = [h.text for h in webdriver.find_elements_by_tag_name("h4")]
    assert "Trainings Effect" not in headings
    assert "Heart Rate" not in headings
    assert "Speed" not in headings
    assert "Cadence" not in headings
    assert "Pace" not in headings
    assert "Temperature" not in headings

    # these should still be there
    assert "Fastest Sections  " in headings
    assert "Laps" in headings

    # again add values for missing attributes
    activity = models.Activity.objects.get()
    activity.trace_file.avg_speed = 1.1
    activity.trace_file.max_speed = 2.2
    activity.trace_file.max_cadence = 3.3
    activity.trace_file.avg_cadence = 3.3
    activity.trace_file.aerobic_training_effect = 4.4
    activity.trace_file.anaerobic_training_effect = 4.4
    activity.trace_file.avg_heart_rate = 5.5
    activity.trace_file.min_heart_rate = 5.5
    activity.trace_file.max_heart_rate = 5.5
    activity.trace_file.min_temperature = 6.6
    activity.trace_file.save()

    # again open activity page
    webdriver.refresh()

    # and verify all headings are back
    headings = [h.text for h in webdriver.find_elements_by_tag_name("h4")]
    assert "Fastest Sections  " in headings
    assert "Laps" in headings
    assert "Speed" in headings
    assert "Pace" in headings
    assert "Temperature" in headings
    assert "Trainings Effect" in headings
    assert "Heart Rate" in headings
    assert "Cadence" in headings


def test_trophy_icon_for_awarded_activity_is_displayed_correctly(db, live_server, webdriver):
    assert models.Activity.objects.count() == 0

    # add activity
    sport = models.Sport.objects.create(name="Swimming", slug="swimming", icon="swimmer", color="#51CBCE")
    activity = models.Activity.objects.create(
        name="Foo",
        sport=sport,
        date=datetime.datetime(2020, 1, 1, 15, 30, 0, tzinfo=pytz.UTC),
        duration=datetime.timedelta(0, 3600),
    )

    activity_url = live_server.url + f"/activity/{activity.pk}"
    webdriver.get(activity_url)
    # neither best sections nor total ascent is available, thus we expect 0 trophies on the activity page
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 0

    # add total ascent to activity
    trace = models.Traces.objects.create(
        path_to_file="dummy/path",
        file_name="foo.baa",
        md5sum="1a2b3c4d5e",
        total_ascent=500,
        total_descent=501,
    )
    activity.trace_file = trace
    activity.save()

    webdriver.get(activity_url)
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 1

    trophy = webdriver.find_element_by_class_name("fa-trophy")
    color = trophy.value_of_css_property("color")
    assert "255, 215, 0" in color
    assert "rgb" in color

    # add best sections
    models.BestSection.objects.create(
        activity=activity,
        kind="fastest",
        distance=1000,
        start=42,
        end=128,
        max_value=123.45,
    )
    webdriver.get(activity_url)
    # since the title of the "fastest section" card will also contain an additional trophy, we now expect 3
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 3


def test_bokeh_lap_button(import_one_activity, live_server, webdriver_firefox, take_screenshot, tmp_path):
    # note: this test is ran with firefox only, since chrome did take screenshots
    # with different colors than expected when running with mac os.
    webdriver = webdriver_firefox()

    import_one_activity("2020-08-20-09-34-33.fit")

    activity = models.Activity.objects.get()
    webdriver.get(live_server.url + f"/activity/{activity.pk}")

    # click two times (on and off) on bokeh button to ensure the plots and the map are in the center of the screen
    webdriver.find_element(By.CSS_SELECTOR, "div.bk-btn:nth-child(1)").click()
    webdriver.find_element(By.CSS_SELECTOR, "div.bk-btn:nth-child(1)").click()

    # test rendering of lap markers by taking screenshots of the page and counting the number of colored pixels
    img_default = "activity_screenshot_default.png"
    take_screenshot(webdriver, name=img_default, path=tmp_path)

    # get the number of pixels in the color of manual and auto lap triggers
    image = Image.open(tmp_path / img_default)
    manual_rgb_color = ImageColor.getcolor(Colors.lap_colors.manual, "RGBA")
    manual_pixel_default = 0
    auto_rgb_color = ImageColor.getcolor(Colors.lap_colors.distance, "RGBA")
    auto_pixel_default = 0
    for pixel in image.getdata():
        if pixel == manual_rgb_color:
            manual_pixel_default += 1
        if pixel == auto_rgb_color:
            auto_pixel_default += 1

    # since manual laps are toggled by default, we expect to find some manual laps to be rendered as both vertical lines
    # in the bokeh plot and circle markers in the leaflet map
    assert manual_pixel_default > 0
    # auto laps are not toggled, thus number of pixles should be 0
    assert auto_pixel_default == 0

    # now lets toggle the auto laps on, take a screenshot and again count the number of colored pixels
    webdriver.find_element(By.CSS_SELECTOR, "div.bk-btn:nth-child(1)").click()

    img_auto_on = "activity_screenshot_auto_on.png"
    take_screenshot(webdriver, name=img_auto_on, path=tmp_path)

    manual_pixel_auto_on = 0
    auto_pixel_auto_on = 0

    image = Image.open(tmp_path / img_auto_on)
    for pixel in image.getdata():
        if pixel == manual_rgb_color:
            manual_pixel_auto_on += 1
        if pixel == auto_rgb_color:
            auto_pixel_auto_on += 1

    # since we didn't touch the manual laps button, number of pixels should still be the same
    assert manual_pixel_auto_on == manual_pixel_default
    # auto laps are now toggled, thus we expect to find some pixels in the respective color
    assert auto_pixel_auto_on > 0

    # now lets toggle the manual laps off and again count the pixels
    webdriver.find_element(By.CSS_SELECTOR, "div.bk-btn:nth-child(2)").click()

    img_manual_off = "activity_screenshot_manual_off.png"
    take_screenshot(webdriver, name=img_manual_off, path=tmp_path)

    manual_pixel_manual_off = 0
    auto_pixel_manual_off = 0

    image = Image.open(tmp_path / img_manual_off)
    for pixel in image.getdata():
        if pixel == manual_rgb_color:
            manual_pixel_manual_off += 1
        if pixel == auto_rgb_color:
            auto_pixel_manual_off += 1

    # since we didn't touch the auto laps button, number of pixels should still be the same
    # (within little variations due to the fact that manual laps could have covered auto lap lines)
    assert (
        auto_pixel_manual_off - auto_pixel_manual_off * 0.1
        < auto_pixel_auto_on
        < auto_pixel_manual_off + auto_pixel_manual_off * 0.1
    )
    # manual pixels are again toggled off and thus we expect to find zero pixels
    assert manual_pixel_manual_off == 0
