from AbstractAdapter import *

class AbstractElementAdapter(AbstractAdapter):

    def __init__(self, gst_element, parent):
        AbstractAdapter.__init__(self, gst_element, parent)


    def get_selection(self):
        return self.gst_object.plugster_data.get_pipeline().plugster_selection


    def is_selected(self):
        return self.get_selection().contains(self.gst_object)
