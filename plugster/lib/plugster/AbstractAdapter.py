import weakref

import pango
import goocanvas
import gst

class AbstractAdapter(goocanvas.Group):

    BASE_PADDING   = 5.0
    DOUBLE_PADDING = 2.0 * BASE_PADDING
    font_height    = 0


    def __init__(self, gst_object, parent):
        goocanvas.Group.__init__(self, parent = parent)
        self.gst_object = weakref.proxy(gst_object, self._on_object_deleted)
        gst_object.plugster_adapter = weakref.proxy(self)
        font_desc = self.get_canvas().get_pango_context().get_font_description()
        self.props.font_desc = font_desc
        if AbstractAdapter.font_height == 0:
            metrics = self.get_canvas().get_pango_context().get_metrics(font_desc, None)
            AbstractAdapter.font_height = float(pango.PIXELS(metrics.get_ascent() + metrics.get_descent()))


    def _on_object_deleted(self, gst_object):
        self.remove()
