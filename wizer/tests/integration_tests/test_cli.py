from workoutizer.__main__ import _get_local_ip_address, _get_latest_version_of


def test__get_local_ip_address():
    ip_address = _get_local_ip_address()
    assert type(ip_address) == str
    assert len(ip_address) >= 8
    assert "." in ip_address


def test__get_latest_version_of():
    # should always be False since I always should have the recent one (github ci also)
    assert _get_latest_version_of("workoutizer") is False

    # should return the latest version, since it was down-pinned
    latest_version = _get_latest_version_of("django-leaflet")
    assert len(latest_version) > 4
    assert "." in latest_version
