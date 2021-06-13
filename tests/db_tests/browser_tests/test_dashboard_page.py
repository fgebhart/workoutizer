import datetime

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import pytest
import pytz

from wkz import configuration
from wkz import models
from wkz.views import get_flat_list_of_pks_of_activities_in_top_awards


def test_dashboard_page_accessible(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # first time running workoutizer will lead to the dashboard page with no data
    h3 = webdriver.find_element_by_css_selector("h3")
    assert h3.text == "No activity data selected for plotting  "


def test_add_activity_button(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # ensure button to create new data is actually redirecting to add activity page
    webdriver.find_element_by_id("add-activity-button").click()
    assert webdriver.current_url == live_server.url + reverse("add-activity")


def test_nav_bar_items(live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))

    # ensure nav bar link to settings page works
    webdriver.find_element_by_id("settings-button").click()
    assert webdriver.current_url == live_server.url + reverse("settings")

    # ensure nav bar link to help page works
    webdriver.find_element_by_id("help-button").click()
    assert webdriver.current_url == live_server.url + reverse("help")


def test_drop_down_visible(live_server, webdriver, settings):
    webdriver.get(live_server.url + reverse("home"))
    days = settings.number_of_days

    dropdown_button = webdriver.find_element_by_id("dropdown-btn")
    assert dropdown_button.text == f"{days} DAYS"


def test_dashboard_page__complete(import_demo_data, live_server, webdriver):
    webdriver.get(live_server.url + reverse("home"))
    assert webdriver.find_element_by_class_name("navbar-brand").text == "Dashboard"

    # check that all activity names are in the table
    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Jogging in Heidelberg" in table_data
    assert "Swimming" in table_data
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Early Morning Cycling in Kochel am See" in table_data
    assert "Noon Hiking in Aftersteg" in table_data
    assert "Noon Hiking in Kornau" in table_data

    # check that the trophy icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0

    # check that sport icons are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-bicycle")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-hiking")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-running")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-swimmer")) > 0

    # check left side bar icons are present
    assert len(webdriver.find_elements_by_class_name("fa-chart-line")) == 2  # sidebar and summary facts
    assert len(webdriver.find_elements_by_class_name("fa-medal")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-plus")) >= 1

    # check icons in top navbar are present
    assert len(webdriver.find_elements_by_class_name("fa-question-circle")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-cog")) == 1

    # check icons in right sidebar are present
    assert len(webdriver.find_elements_by_class_name("fa-hashtag")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-road")) == 1
    assert len(webdriver.find_elements_by_class_name("fa-history")) == 3

    # verify that each activity which is in top score has an award and also is displayed with a trophy
    href = [a.get_attribute("href") for a in webdriver.find_elements_by_tag_name("a")]
    pks = []
    for url in href:
        if url is not None:
            if "/activity/" in url:
                pks.append(url.split("/")[-1])
    pks = set(pks)

    top_award_pks = []
    sport_slugs = [
        sport.slug for sport in models.Sport.objects.filter(evaluates_for_awards=True).exclude(name="unknown")
    ]

    for sport in sport_slugs:
        for bs in configuration.best_sections:
            for distance in bs["distances"]:
                top_awards = models.BestSection.objects.filter(
                    activity__sport__slug=sport,
                    activity__evaluates_for_awards=True,
                    kind=bs["kind"],
                    distance=distance,
                ).order_by("-max_value")[: configuration.rank_limit]
                top_award_pks += [str(award.activity.pk) for award in top_awards]
    top_award_pks = list(set(top_award_pks))

    expected_num_of_trophies = 0
    for pk in pks:
        if pk in top_award_pks:
            expected_num_of_trophies += 1

    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == expected_num_of_trophies

    # check that "made with love" text is not present
    with pytest.raises(NoSuchElementException):
        webdriver.find_element(By.CLASS_NAME, "credits")


def test_dashboard__infinite_scroll(tracks_in_tmpdir, live_server, webdriver, insert_activity):
    rows_per_page = configuration.number_of_rows_per_page_in_table
    # insert more activities than the currently configured value of rows
    # per page in order to be  able to trigger the htmx ajax request
    nr_of_inserted_activities = rows_per_page + 5
    for i in range(nr_of_inserted_activities):
        insert_activity(name=f"Dummy Activity {i}")

    assert models.Activity.objects.count() == nr_of_inserted_activities
    webdriver.get(live_server.url + reverse("home"))

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


def test_trophy_icon_for_awarded_activities_in_table_are_displayed_correctly(db, live_server, webdriver):
    assert models.Activity.objects.count() == 0

    # add a few activities
    sport = models.Sport.objects.create(name="Swimming", slug="swimming", icon="swimmer", color="#51CBCE")
    activity_1 = models.Activity.objects.create(
        name="Activity 1",
        sport=sport,
        date=datetime.datetime(2020, 1, 1, 15, 30, 0, tzinfo=pytz.UTC),
        duration=datetime.timedelta(0, 3600),
    )
    activity_2 = models.Activity.objects.create(
        name="Activity 2",
        sport=sport,
        date=datetime.datetime(2020, 1, 2, 15, 30, 0, tzinfo=pytz.UTC),
        duration=datetime.timedelta(0, 3600),
    )
    activity_3 = models.Activity.objects.create(
        name="Activity 3",
        sport=sport,
        date=datetime.datetime(2020, 1, 3, 15, 30, 0, tzinfo=pytz.UTC),
        duration=datetime.timedelta(0, 3600),
    )
    assert models.Sport.objects.count() == 1
    assert models.Activity.objects.count() == 3

    # verify no trophies are present by now
    webdriver.get(live_server.url + reverse("home"))
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 0

    # check that activities are already displayed in the table
    td = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert activity_1.name in td
    assert activity_2.name in td
    assert activity_3.name in td

    assert get_flat_list_of_pks_of_activities_in_top_awards() == []

    # now add best sections to activity 1 ...
    models.BestSection.objects.create(
        activity=activity_1,
        kind="fastest",
        distance=1000,
        start=42,
        end=128,
        max_value=123.45,
    )
    webdriver.get(live_server.url + reverse("home"))
    # ... and verify that 1 trophy is present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 1
    assert get_flat_list_of_pks_of_activities_in_top_awards() == [activity_1.pk]

    # add best section to activity 2 ...
    models.BestSection.objects.create(
        activity=activity_2,
        kind="fastest",
        distance=5000,
        start=43,
        end=129,
        max_value=99.99,
    )
    webdriver.get(live_server.url + reverse("home"))
    # ... and verify that 2 trophies are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 2
    assert get_flat_list_of_pks_of_activities_in_top_awards() == [activity_1.pk, activity_2.pk]

    # also add total ascent value to activity 3...
    trace = models.Traces.objects.create(
        path_to_file="dummy/path",
        file_name="foo.baa",
        md5sum="1a2b3c4d5e",
        total_ascent=500,
        total_descent=501,
    )
    activity_3.trace_file = trace
    activity_3.save()
    webdriver.get(live_server.url + reverse("home"))
    # ... and verify that 3 trophies are present
    assert len(webdriver.find_elements_by_class_name("fa-trophy")) == 3
    assert get_flat_list_of_pks_of_activities_in_top_awards() == [activity_1.pk, activity_2.pk, activity_3.pk]
