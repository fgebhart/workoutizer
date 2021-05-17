from django.urls import reverse

from selenium.webdriver.common.by import By

from wkz import models
from wkz import configuration


def test_awards_page__complete(import_demo_data, live_server, webdriver):
    """
    Check the content of the awards page by:
    1. assert existence of different html tags,...
    2. disable awards for a bunch of activities and verify that the number of trophies changed on the awards page
    3. disable awards for entire sport and verify that the number of trophies changed on the awards page
    """

    webdriver.get(live_server.url + reverse("awards"))

    # 1. assert existence of different html tags,...
    table_header = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "RANK" in table_header
    assert "DISTANCE" in table_header
    assert "DATE" in table_header
    assert "ACTIVITY" in table_header
    assert "SPEED  " in table_header

    h4 = [h4.text for h4 in webdriver.find_elements_by_tag_name("h4")]
    # note hiking activities won't show up, since they are disabled for awards in initial_data_handler
    assert "Hiking  " not in h4
    assert "Jogging  " in h4
    assert "Cycling  " in h4

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "Noon Hiking in Aftersteg" not in links
    assert "Noon Hiking in Kornau" not in links
    assert "Noon Hiking in Bad Schandau" not in links
    assert "Noon Jogging in Mirow" in links
    assert "Noon Jogging in Heidelberg" in links
    assert "Noon Cycling in Hinterzarten" in links
    assert "Noon Cycling in Bad Schandau" in links
    assert "Noon Cycling in Dahn" in links

    table_data = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]
    assert "Noon Cycling in Bad Schandau" in table_data
    assert "Noon Cycling in Hinterzarten" in table_data
    assert "Noon Cycling in Dahn" in table_data
    assert "Noon Jogging in Heidelberg" in table_data
    assert "Noon Jogging in Mirow" in table_data
    assert "42.2 km/h" in table_data

    # fastest sections distances
    assert "1km" in table_data
    assert "2km" in table_data
    assert "3km" in table_data
    assert "5km" in table_data
    assert "10km" in table_data

    assert len(webdriver.find_elements_by_class_name("fa-mountain")) > 0
    assert len(webdriver.find_elements_by_class_name("fa-tachometer-alt")) > 0

    first_num_trophies = len(webdriver.find_elements_by_class_name("fa-trophy"))
    assert first_num_trophies > 0

    # 2. disable awards for a few jogging activities and verify that the number of trophies changed on the awards page
    sport = models.Sport.objects.get(slug="jogging")
    activities = models.Activity.objects.filter(sport=sport)[:2]

    for activity in activities:
        # verify that chosen activity actually has at least one trophy
        webdriver.get(live_server.url + f"/activity/{activity.pk}")
        assert webdriver.current_url == f"{live_server.url}/activity/{activity.pk}"
        assert len(webdriver.find_elements_by_class_name("fa-trophy")) > 0

        activity.evaluates_for_awards = False
        activity.save()

    # reconnect to awards page
    webdriver.get(live_server.url + reverse("awards"))
    assert webdriver.current_url == f"{live_server.url}/awards/"

    second_num_trophies = len(webdriver.find_elements_by_class_name("fa-trophy"))
    assert second_num_trophies > 0
    # verify that we now have less awards
    assert first_num_trophies > second_num_trophies

    # 3. disable awards for entire sport and verify that the number of trophies changed on the awards page
    sport = models.Sport.objects.get(slug="cycling")
    sport.evaluates_for_awards = False
    sport.save()

    # reconnect to awards page
    webdriver.get(live_server.url + reverse("awards"))
    assert webdriver.current_url == f"{live_server.url}/awards/"

    third_num_trophies = len(webdriver.find_elements_by_class_name("fa-trophy"))
    assert third_num_trophies > 0
    # verify that we now have less awards
    assert first_num_trophies > second_num_trophies > third_num_trophies


def test_correct_activities_are_listed_on_awards_page(import_demo_data, live_server, webdriver):
    # first check activities listed in fastest awards
    webdriver.get(live_server.url + reverse("awards"))

    th = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "RANK" in th
    assert "DISTANCE" in th
    assert "DATE" in th
    assert "ACTIVITY" in th
    assert "SPEED  " in th

    fastest_top_awards = []
    for distance in configuration.fastest_distances:
        awards = models.BestSection.objects.filter(
            distance=distance,
            activity__evaluates_for_awards=True,
            kind="fastest",
        ).order_by("-max_value")[: configuration.rank_limit]
        fastest_top_awards += list(awards)

    # get table content
    td = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]

    # verify that these activities are present in the table content
    activity_names = [award.activity.name for award in fastest_top_awards]
    for name in activity_names:
        assert name in td

    max_value = [f"{round(award.max_value * 3.6, 1)} km/h" for award in fastest_top_awards]
    for value in max_value:
        assert value in td

    activity_dates = [award.activity.date.date().strftime("%b %d, %Y") for award in fastest_top_awards]
    for date in activity_dates:
        assert date in td

    # now check the same for the climb awards, first go to climb tab
    webdriver.find_element(By.LINK_TEXT, "Climb Awards").click()

    th = [cell.text for cell in webdriver.find_elements_by_tag_name("th")]
    assert "RANK" in th
    assert "DISTANCE" in th
    assert "DATE" in th
    assert "ACTIVITY" in th
    assert "CLIMB  " in th

    climb_top_awards = []
    for distance in configuration.climb_distances:
        awards = models.BestSection.objects.filter(
            distance=distance,
            activity__evaluates_for_awards=True,
            kind="climb",
        ).order_by("-max_value")[: configuration.rank_limit]
        climb_top_awards += list(awards)

    # get table content
    td = [cell.text for cell in webdriver.find_elements_by_tag_name("td")]

    # verify that these activities are present in the table content
    activity_names = [award.activity.name for award in climb_top_awards]
    for name in activity_names:
        assert name in td

    activity_dates = [award.activity.date.date().strftime("%b %d, %Y") for award in climb_top_awards]
    for date in activity_dates:
        assert date in td

    max_value = [f"{round(award.max_value, 2)} m/min" for award in climb_top_awards]
    for value in max_value:
        assert value in td
