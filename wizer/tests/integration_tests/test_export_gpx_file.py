import os
from lxml import etree

from wizer.file_helper.gpx_exporter import save_activity_to_gpx_file


def test_save_activity_to_gpx_file(activity):
    path = save_activity_to_gpx_file(activity)
    assert os.path.isfile(path)
    assert path.split("/")[-1] == "2020-07-07_evening-cycling-along-the-river.gpx"
    # verify xml file is well formed this would raise lxml.etree.XMLSyntaxError if not
    etree.parse(path)
