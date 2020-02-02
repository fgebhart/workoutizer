from wizer.file_helper.gpx_parser import calc_distance_of_points


def test_calc_distance_of_points():
    assert int(calc_distance_of_points([(41.49008, -71.312796), (41.499498, -81.695391)])) == int(667)
