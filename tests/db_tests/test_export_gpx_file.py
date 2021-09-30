import os

from lxml import etree

from wkz.io.gpx_exporter import save_activity_to_gpx_file


def test_save_activity_to_gpx_file(activity):
    path = save_activity_to_gpx_file(activity)
    assert os.path.isfile(path)
    assert os.path.basename(path) == "2020-07-07_evening-cycling-along-the-river.gpx"
    # verify xml file is well formed this would raise lxml.etree.XMLSyntaxError if not
    etree.parse(path)
