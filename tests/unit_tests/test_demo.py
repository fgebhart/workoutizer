from wkz.demo import copy_demo_fit_files_to_track_dir


def test_copy_demo_fit_files_to_track_dir__basic(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # create some dummy files
    file_1 = src_dir / "file_1.txt"
    file_1.write_text("foo")
    assert file_1.read_text() == "foo"
    file_2 = src_dir / "file_2.txt"
    file_2.write_text("baa")
    assert file_2.read_text() == "baa"

    # copy all files
    copy_demo_fit_files_to_track_dir(source_dir=str(src_dir), targe_dir=str(target_dir))

    copied_file_1 = target_dir / "file_1.txt"
    copied_file_2 = target_dir / "file_2.txt"

    assert copied_file_1.is_file()
    assert copied_file_2.is_file()

    assert copied_file_1.read_text() == "foo"
    assert copied_file_2.read_text() == "baa"


def test_copy_demo_fit_files_to_track_dir__filter_files(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # create some dummy files
    file_1 = src_dir / "file_1.txt"
    file_1.write_text("foo")
    file_2 = src_dir / "file_2.txt"
    file_2.write_text("baa")

    # copy just file_1
    copy_demo_fit_files_to_track_dir(source_dir=src_dir, targe_dir=target_dir, list_of_files_to_copy=[file_1])

    copied_file_1 = target_dir / "file_1.txt"
    copied_file_2 = target_dir / "file_2.txt"

    assert copied_file_1.is_file()
    assert copied_file_1.read_text() == "foo"
    assert not copied_file_2.is_file()


def test_copy_demo_fit_files_to_track_dir__with_pre_existing_dir(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # add traces dir within target and src dir
    trace_dir = target_dir / "traces"
    trace_dir.mkdir()
    src_trace_dir = src_dir / "traces"
    src_trace_dir.mkdir()

    # create some dummy files
    file_1 = src_trace_dir / "file_1.txt"
    file_1.write_text("foo")
    file_2 = src_trace_dir / "file_2.txt"
    file_2.write_text("baa")

    # copy files (this would fail without 'dirs_exist_ok=True' because trace does exist already)
    copy_demo_fit_files_to_track_dir(source_dir=str(src_dir), targe_dir=str(target_dir))

    copied_file_1 = trace_dir / "file_1.txt"
    copied_file_2 = trace_dir / "file_2.txt"

    assert copied_file_1.is_file()
    assert copied_file_1.read_text() == "foo"
    assert copied_file_2.is_file()
    assert copied_file_2.read_text() == "baa"
