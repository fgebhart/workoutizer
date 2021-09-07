from wkz.tools.utils import get_local_ip_address, limit_string, sanitize


def test_sanitize():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize("activity1/3") == "activity1-3"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_limit_string():
    assert limit_string(string="12345", max_length=10) == "12345"
    assert limit_string(string="12345", max_length=2) == "1...5"
    assert limit_string(string="12345", max_length=3) == "1...5"
    assert limit_string(string="12345", max_length=4) == "12...45"
    assert limit_string(string="12345", max_length=5) == "12345"
    assert limit_string(string="some super duper long string", max_length=12) == "some s...string"


def test__get_local_ip_address():
    ip_address = get_local_ip_address()
    assert type(ip_address) == str
    assert len(ip_address) >= 8
    assert "." in ip_address
