import xml.etree.cElementTree

import gst

import Definitions
from ElementData import *

class XmlPipelineDeserializer(object):

    def __init__(self):
        object.__init__(self)
        self._reset()


    def _reset(self):
        self._data = {}


    def _gst(self, tag):
        return "{" + Definitions.GST_XML_NAMESPACE + "}" + tag


    def _plugster(self, tag):
        return "{" + Definitions.PLUGSTER_XML_NAMESPACE + "}" + tag


    def load(self, filepath):
        self._reset()
        doc = xml.etree.cElementTree.parse(filepath)
        root = doc.getroot()
        if root.tag == "gstreamer":
            elt = root.find(self._gst("element"))
            self._parse_element(elt, True)

        gst_xml = gst.XML()
        gst_xml.connect('object-loaded', self._load_plugster_data)
        if gst_xml.parse_file(filepath, Definitions.ROOT_PIPELINE_NAME):
            elements = gst_xml.get_topelements()
            if len(elements) > 0:
                return elements[0]
        return None


    def _parse_element(self, elt, root):
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
                self._parse_element(child, False)


    def _load_plugster_data(self, xml_node, gst_object, user_data):
        name = gst_object.get_name()
        if name in self._data:
            xml_data = self._data[name]
            data = ElementData(gst_object)
            data.x = xml_data[0]
            data.y = xml_data[1]
