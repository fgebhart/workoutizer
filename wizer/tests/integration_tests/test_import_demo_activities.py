from wizer import models


def test_import_of_demo_activities(import_demo_data, client):
    # verify activities got imported
    all_activities = models.Activity.objects.all()
    assert len(all_activities) == 19

    for activity in all_activities:
        response = client.get(f"/activity/{activity.pk}")
        assert response.status_code == 200

    swimming = models.Activity.objects.filter(sport__slug="swimming")
    assert len(swimming) == 9

    jogging = models.Activity.objects.filter(sport__slug="jogging")
    assert len(jogging) == 4

    cycling = models.Activity.objects.filter(sport__slug="cycling")
    assert len(cycling) == 3

    hiking = models.Activity.objects.filter(sport__slug="hiking")
    assert len(hiking) == 3

    # verify that best sections got parsed and imported
    best_sections = models.BestSection.objects.all()
    assert len(best_sections) == 61

    fastest_sections = models.BestSection.objects.filter(section_type="fastest")
    assert len(fastest_sections) == 61
