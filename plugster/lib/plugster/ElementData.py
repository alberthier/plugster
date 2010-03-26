import weakref

import gobject
import gst

class ElementData(gobject.GObject):

    XML_NS           = "plugster";
    XML_COORDS_TAG   = "coords";
    XML_HREF         = "http://gstreamer.net/plugster/1.0/";
    XML_COORDS_X_TAG = "x";
    XML_COORDS_Y_TAG = "y";


    __gsignals__ = {
        'selected-state-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }


    def __init__(self, element):
        gobject.GObject.__init__(self)
        self.element = weakref.proxy(element)
        self.x = 0
        self.y = 0
        element.plugster_data = self


    @staticmethod
    def load(xml_node, gst_object, user_data, data_loader):
        xml_data = data_loader.get_data(gst_object.get_name())
        data = ElementData(gst_object)
        if xml_data != None:
            data.x = xml_data[0]
            data.y = xml_data[1]


    def get_pipeline(self):
        if isinstance(self.element, gst.Pipeline):
            return self.element
        else:
            return self.element.get_parent().plugster_data.get_pipeline()

