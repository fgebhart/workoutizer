from workoutizer.__main__ import _get_local_ip_address


def test__get_local_ip_address():
    ip_address = _get_local_ip_address()
    assert type(ip_address) == str
    assert len(ip_address) >= 8
    assert "." in ip_address
