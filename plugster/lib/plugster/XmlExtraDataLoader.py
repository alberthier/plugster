import xml.etree.cElementTree

from Definitions import *

class XmlExtraDataLoader(object):

    def __init__(self):
        object.__init__(self)
        self._reset()


    def _reset(self):
        self._data = {}


    def _gst(self, tag):
        return "{" + GST_XML_NAMESPACE + "}" + tag


    def _plugster(self, tag):
        return "{" + PLUGSTER_XML_NAMESPACE + "}" + tag


    def load(self, filepath):
        self._reset()
        doc = xml.etree.cElementTree.parse(filepath)
        root = doc.getroot()
        if root.tag == "gstreamer":
            elt = root.find(self._gst("element"))
            self.parse_element(elt, True)


    def parse_element(self, elt, root):
        if not root:
            name_node = elt.find(self._gst("name"))
            data_node = elt.find(self._plugster("data"))
            if data_node != None:
                data_x_node = data_node.find(self._plugster("x"))
                data_y_node = data_node.find(self._plugster("y"))
                if name_node != None and data_x_node != None and data_y_node != None:
                    self._data[name_node.text] = (int(data_x_node.text.strip()), int(data_y_node.text.strip()))
        children_node = elt.find(self._gst("children"))
        if children_node != None:
            for child in children_node.getchildren():
                self.parse_element(child, False)


    def get_data(self, name):
        if name in self._data:
            return self._data[name]
        else:
            return None
