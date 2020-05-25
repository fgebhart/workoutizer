from wizer.file_helper.reimporter import _values_equal


def test__values_equal():
    assert _values_equal(3, 3) is True
    assert _values_equal(3., 3) is True
    assert _values_equal(3., "3") is True
    assert _values_equal("3", 3) is True
    assert _values_equal([1, 2, 3], "[1, 2, 3]") is True
    assert _values_equal('[0.0, 1.016, 1.244]', [None, 1.016, 1.244]) is False
    assert _values_equal(1, 2.) is False
    assert _values_equal(None, 2.) is False
