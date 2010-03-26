import gtk
import goocanvas

from AbstractElementAdapter import *
from ElementAdapter import *
from PipelineCanvas import *
from Selection import *

class PipelineAdapter(AbstractElementAdapter):

    element_numbers = {}

    def __init__(self, pipeline, canvas):
        AbstractElementAdapter.__init__(self, pipeline, canvas.get_root_item())
        self.elements_layer = goocanvas.Group(parent = self)
        self.links_layer = goocanvas.Group(parent = self)

        pipeline.connect('element-added', self._on_element_added)
        self.on_drag_data_received_id = canvas.connect('drag-data-received', self._create_new_element)
        self.on_button_press_event_id = canvas.connect('button-press-event', self._on_button_pressed)

        self._on_end_drag_id = None
        self._on_drag_move_id = None
        self._drag_x = 0;
        self._drag_y = 0;
        self._global_dx = 0;
        self._global_dy = 0;

        for child in self.gst_object:
            self._on_element_added(self.gst_object, child)


    def _on_object_deleted(self, gst_object):
        canvas = self.get_canvas()
        canvas.disconnect(self.on_drag_data_received_id)
        canvas.disconnect(self.on_button_press_event_id)
        AbstractElementAdapter._on_object_deleted(self, gst_object)


    def _create_new_element(self, widget, drag_context, x, y, selection_data, info, timestamp):
        plugster_atom = gtk.gdk.atom_intern("application/x-plugster-element-factory", True)
        if selection_data.type == plugster_atom:
            factory_name = selection_data.data
            drag_context.finish(True, False, timestamp)
            if factory_name in PipelineAdapter.element_numbers:
                n = PipelineAdapter.element_numbers[factory_name] + 1
            else:
                n = 1
            PipelineAdapter.element_numbers[factory_name] = n
            elt = gst.element_factory_make(factory_name, "{0}{1}".format(factory_name, n))
            data = ElementData(elt)
            data.x = x + PipelineCanvas.place_coord_on_grid(x)
            data.y = y + PipelineCanvas.place_coord_on_grid(y)
            self.gst_object.add(elt)
            # Use data.element to use the weak ref in the selection
            self.gst_object.plugster_selection.select(data.element)


    def _on_element_added(self, pipeline, element):
        ElementAdapter(element, self.elements_layer)


    def _on_button_pressed(self, widget, event):
        if event.button == 1: # Left button
            (x, y) = event.get_coords()
            if self.get_canvas().get_items_at(x, y, False) == None:
                self.gst_object.plugster_selection.clear()
        return False
