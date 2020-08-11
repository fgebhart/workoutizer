from wizer.tools.utils import sanitize, remove_nones_from_string, remove_nones_from_list, cut_list_to_have_same_length, \
    extend_list_to_have_length


def test_remove_nones_from_string():
    assert remove_nones_from_string("fooNoneboo") == "fooboo"
    assert remove_nones_from_string("asdf None asdf") == "asdf asdf"
    assert remove_nones_from_string("[123, None, 456]") == "[123, 456]"
    assert remove_nones_from_string("[26, 0, None]") == "[26, 0]"
    assert remove_nones_from_string("[26, None, 0, None]") == "[26, 0]"


def test_sanitize():
    assert sanitize("Lore Ipsum") == "lore-ipsum"
    assert sanitize("some-words") == "some-words"
    assert sanitize("activity1/3") == "activity1-3"
    assert sanitize(1) == "1"
    assert sanitize(0.123) == "0.123"
    assert sanitize(True) == "true"


def test_remove_nones_from_list():
    assert remove_nones_from_list([None]) == []
    assert remove_nones_from_list([None, 1, 2, "a"]) == [1, 2, "a"]
    assert remove_nones_from_list([None, 1, None, 2]) == [1, 2]


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


def test_extend_list_to_have_length():
    assert extend_list_to_have_length(length=5, input_list=[1., 2., 3.]) == [1., 1.5, 2., 2.5, 3.]
    assert extend_list_to_have_length(length=9, input_list=[1., 2., 3., 4., 5.]) == [1., 1.5, 2., 2.5, 3., 3.5, 4., 4.5,
                                                                                     5.]
    assert extend_list_to_have_length(length=2, input_list=[]) == []
