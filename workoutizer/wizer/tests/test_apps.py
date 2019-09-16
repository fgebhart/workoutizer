from wizer.apps import map_sport_name

sport_map = {
    'Jogging': ['jogging', 'running'],
}


def test_map_sport_name():
    assert map_sport_name('running', sport_map) == "Jogging"
    assert map_sport_name('Running', sport_map) == "Jogging"
