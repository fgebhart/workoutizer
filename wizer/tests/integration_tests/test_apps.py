from wizer.apps import map_sport_name, sport_naming_map, _was_runserver_triggered


def test_map_sport_name():
    assert map_sport_name('running', sport_naming_map) == "Jogging"
    assert map_sport_name('Running', sport_naming_map) == "Jogging"
    assert map_sport_name('swim', sport_naming_map) == "Swimming"
    assert map_sport_name('SUP', sport_naming_map) == "unknown"


def test__was_runserver_triggered():
    args = ['runserver']
    assert _was_runserver_triggered(args) is True
    args = ['runserver', 'help']
    assert _was_runserver_triggered(args) is False
    args = ['manage', 'runserver 0.0.0.0:8000 --noreload']
    assert _was_runserver_triggered(args) is True
