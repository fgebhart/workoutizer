from wizer.apps import map_sport_name, sport_naming_map


def test_map_sport_name():
    assert map_sport_name('running', sport_naming_map) == "Jogging"
    assert map_sport_name('Running', sport_naming_map) == "Jogging"
    assert map_sport_name('swim', sport_naming_map) == "Swimming"
    assert map_sport_name('SUP', sport_naming_map) == "unknown"
