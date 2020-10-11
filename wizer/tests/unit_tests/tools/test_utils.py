from wizer.tools.utils import sanitize, cut_list_to_have_same_length, limit_string


def test_sanitize():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize("activity1/3") == "activity1-3"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_cut_list_to_have_same_length():
    # mode: cut beginning
    assert cut_list_to_have_same_length([1, 2, 3, 4, 5], [3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert cut_list_to_have_same_length([3, 4, 5], [1, 2, 3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert cut_list_to_have_same_length([3, 4, 5], [3, 4, 5]) == ([3, 4, 5], [3, 4, 5])
    assert cut_list_to_have_same_length([3], []) == ([], [])
    # mode: fill end of shorter list with same as last item
    assert cut_list_to_have_same_length([1, 2, 3], [1], mode="fill end") == ([1, 2, 3], [1, 1, 1])
    assert cut_list_to_have_same_length([1], [1, 2, 3], mode="fill end") == ([1, 1, 1], [1, 2, 3])
    assert cut_list_to_have_same_length([1], [1, 2, 3], mode="fill end", modify_only_list2=True) == ([1], [1, 2, 3])
    assert cut_list_to_have_same_length(['a'], ['a', 'b', 'c'], mode="fill end") == (['a', 'a', 'a'], ['a', 'b', 'c'])
    assert cut_list_to_have_same_length([3, 4, 5], [3, 4, 5], mode="fill end") == ([3, 4, 5], [3, 4, 5])


def test_limit_string():
    assert limit_string(string="12345", max_length=10) == "12345"
    assert limit_string(string="12345", max_length=2) == "1...5"
    assert limit_string(string="12345", max_length=3) == "1...5"
    assert limit_string(string="12345", max_length=4) == "12...45"
    assert limit_string(string="12345", max_length=5) == "12345"
    assert limit_string(string="some super duper long string", max_length=12) == "some s...string"