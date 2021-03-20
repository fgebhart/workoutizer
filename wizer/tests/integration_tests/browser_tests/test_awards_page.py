from django.urls import reverse

from selenium.webdriver.common.by import By

from wizer import models
from wizer.awards_views import awards_info_texts


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
    assert "Rank" in table_header
    assert "Distance" in table_header
    assert "Date" in table_header
    assert "Activity" in table_header
    assert "Speed" in table_header

    assert "Your Awards" in webdriver.find_element_by_tag_name("h3").text

    h4 = [h4.text for h4 in webdriver.find_elements_by_tag_name("h4")]
    # note hiking activities won't show up, since they are disabled for awards in initial_data_handler
    assert "Hiking  " not in h4
    assert "Jogging  " in h4
    assert "Cycling  " in h4

    links = [a.text for a in webdriver.find_elements_by_tag_name("a")]
    assert "  Add Activity" in links
    assert "  Workoutizer  " in links
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
    assert "42.7 km/h" in table_data

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
    # check that correct activities are actually listed in awards page
    from IPython import embed

    embed()
    pass


def test_awards_kind_tabs(live_server, webdriver, take_screenshot):
    webdriver.get(live_server.url + reverse("awards"))
    p1 = [p.text for p in webdriver.find_elements_by_tag_name("p")]

    # general text on best sections should be present
    assert awards_info_texts["general"] in p1

    # fastest sections text should be present, since fastest sections tab is the active one
    assert awards_info_texts["fastest"] in p1

    # climb section text should not be present by now
    assert awards_info_texts["climb"] not in p1

    # click on climb sections tab
    webdriver.find_element(By.LINK_TEXT, "Best Climb Sections").click()
    p2 = [p.text for p in webdriver.find_elements_by_tag_name("p")]

    # climb section text should now be present
    assert awards_info_texts["climb"] in p2

    # and velocity text should now be gone
    assert awards_info_texts["fastest"] not in p2
