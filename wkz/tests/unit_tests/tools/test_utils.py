import os
import shutil

from wkz.tools.utils import (
    sanitize,
    cut_list_to_have_same_length,
    limit_string,
    get_local_ip_address,
    files_are_same,
)


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
    assert cut_list_to_have_same_length(["a"], ["a", "b", "c"], mode="fill end") == (["a", "a", "a"], ["a", "b", "c"])
    assert cut_list_to_have_same_length([3, 4, 5], [3, 4, 5], mode="fill end") == ([3, 4, 5], [3, 4, 5])


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


def test_files_are_same(tmpdir, test_data_dir):
    # copy a file to temp dir for comparison
    file_a = os.path.join(test_data_dir, "example.fit")
    file_b = os.path.join(tmpdir, "example.fit")
    shutil.copy2(src=file_a, dst=file_b)

    # files are the same
    assert files_are_same(file_a, file_b) is True

    file_c = os.path.join(test_data_dir, "example.gpx")
    # files are not the same
    assert files_are_same(file_a, file_c) is False
