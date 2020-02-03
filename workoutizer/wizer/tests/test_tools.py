from wizer.tools.utils import sanitize, insert_current_date_into_gpx


def test_sanitze():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_insert_current_date_into_gpx():
    assert insert_current_date_into_gpx