from wizer.file_helper.fit_collector import _find_complete_garmin_device_path


def test__find_complete_garmin_device_path(tmpdir):

    # no device path is available, expect to get None
    assert _find_complete_garmin_device_path(tmpdir) is None

    # dummy device path is available, expect to get it
    device_path = tmpdir.mkdir("mtp:host=092e_4b58_0000c4fa0519")
    assert _find_complete_garmin_device_path(tmpdir) == device_path
