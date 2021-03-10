from wizer.watchdogs import _was_runserver_triggered


def test__was_runserver_triggered():
    args = ["runserver"]
    assert _was_runserver_triggered(args) is True
    args = ["runserver", "help"]
    assert _was_runserver_triggered(args) is False
    args = ["runserver", "--help"]
    assert _was_runserver_triggered(args) is False
    args = ["manage", "runserver", "0.0.0.0:8000", "--noreload"]
    assert _was_runserver_triggered(args) is True
