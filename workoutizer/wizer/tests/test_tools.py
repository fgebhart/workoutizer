
from workoutizer.wizer.tools import sanitize


def test_sanitze():
    assert sanitize("Lore Ipsum") == "lore_ipsum"
    assert sanitize("some_words") == "some_words"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"
