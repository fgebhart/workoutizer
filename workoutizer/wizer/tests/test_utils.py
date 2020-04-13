from wizer.tools.utils import sanitize, remove_nones_from_string, remove_nones_from_list, ensure_lists_have_same_length


def test_remove_nones_from_string():
    assert remove_nones_from_string("fooNoneboo") == "fooboo"
    assert remove_nones_from_string("asdf None asdf") == "asdf asdf"
    assert remove_nones_from_string("[123, None, 456]") == "[123, 456]"
    assert remove_nones_from_string("[26, 0, None]") == "[26, 0]"
    assert remove_nones_from_string("[26, None, 0, None]") == "[26, 0]"


def test_sanitze():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_remove_nones_from_list():
    assert remove_nones_from_list([None]) == []
    assert remove_nones_from_list([None, 1, 2, "a"]) == [1, 2, "a"]
    assert remove_nones_from_list([None, 1, None, 2]) == [1, 2]


def test_ensure_list_have_same_length():
    # mode: cut beginning
    assert ensure_lists_have_same_length([1, 2, 3, 4, 5], [3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert ensure_lists_have_same_length([3, 4, 5], [1, 2, 3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert ensure_lists_have_same_length([3, 4, 5], [3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert ensure_lists_have_same_length([3], []) == ([], [])
    # mode: fill end of shorter list with same as last item
    assert ensure_lists_have_same_length([1, 2, 3], [1], mode="fill end") == ([1, 2, 3], [1, 1, 1])
    assert ensure_lists_have_same_length([1], [1, 2, 3], mode="fill end") == ([1, 1, 1], [1, 2, 3])
    assert ensure_lists_have_same_length([1], [1, 2, 3], mode="fill end", modify_only_list2=True) == ([1], [1, 2, 3])
    assert ensure_lists_have_same_length(['a'], ['a', 'b', 'c'], mode="fill end") == (['a', 'a', 'a'], ['a', 'b', 'c'])
    assert ensure_lists_have_same_length([3, 4, 5], [3, 4, 5], mode="fill end") == ([3, 4, 5], [3, 4, 5])
