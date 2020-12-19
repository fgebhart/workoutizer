from workoutizer.__main__ import _get_local_ip_address, _get_latest_version_of


def test__get_local_ip_address():
    ip_address = _get_local_ip_address()
    assert type(ip_address) == str
    assert len(ip_address) >= 8
    assert "." in ip_address


def test__get_latest_version_of():
    # basic sanity check, because actual versions might always change
    latest_version = _get_latest_version_of("django-leaflet")
    assert len(latest_version) > 4
    assert "." in latest_version
