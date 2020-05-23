from wizer.file_helper.reimporter import _values_equal


def test__values_equal():
    assert _values_equal(3, 3) is True
    assert _values_equal(3., 3) is True
    assert _values_equal(3., "3") is True
    assert _values_equal("3", 3) is True
    assert _values_equal([1, 2, 3], "[1, 2, 3]")
    assert _values_equal(1, 2.) is False
