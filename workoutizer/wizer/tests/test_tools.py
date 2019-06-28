from workoutizer.wizer.tools import sanitize
from workoutizer.wizer.gpx_converter import calc_distance_of_points


def test_sanitze():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_calc_distance_of_points():
    assert calc_distance_of_points([(41.49008, -71.312796), (41.499498, -81.695391)]) == 866.4554329098685
