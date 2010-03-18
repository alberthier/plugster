import gtk
import pango
import goocanvas
import gst

from PipelineCanvas import *
from AbstractElementAdapter import *
from PadAdapter import *

class ElementAdapter(AbstractElementAdapter):

    def __init__(self, gst_element, layer):
        AbstractElementAdapter.__init__(self, gst_element, layer)

        self.set_property('tooltip', self.gst_object.get_factory().get_description())

        self.gst_object.connect('pad-added', self._on_pad_added)
        self.gst_object.connect('no-more-pads', self._relayout)
        self.connect('button-press-event', self._on_start_drag)

        data = self.gst_object.plugster_data
        data.connect('selected-state-changed', self._update_title_background)
        style = self.get_canvas().get_style()
        font_desc = self.get_property('font-desc')
        font_desc.set_weight(pango.WEIGHT_BOLD)

        self.background_rect = goocanvas.Rect(parent = self,
                                              fill_color = style.bg[gtk.STATE_NORMAL],
                                              line_width = 0.0,
                                              radius_x = AbstractAdapter.DOUBLE_PADDING,
                                              radius_y = AbstractAdapter.DOUBLE_PADDING)
        self.title_background = goocanvas.Path(parent = self,
                                               data = "m 0 0",
                                               line_width = 0.0)
        self.title = goocanvas.Text(parent = self,
                                    font_desc = font_desc,
                                    y = AbstractAdapter.BASE_PADDING,
                                    alignment = pango.ALIGN_CENTER)
        self.bounding_rect = goocanvas.Rect(parent = self,
                                            stroke_color = style.dark[gtk.STATE_NORMAL],
                                            line_width = 2.0,
                                            radius_x = AbstractAdapter.DOUBLE_PADDING,
                                            radius_y = AbstractAdapter.DOUBLE_PADDING)

        for pad in self.gst_object.pads():
            self._on_pad_added(self.gst_object, pad)

        self._relayout(self.gst_object)
        self.translate(data.x, data.y)


    def _on_pad_added(self, element, pad):
        PadAdapter(pad, self)


    def _relayout(self, element):
        style = self.get_canvas().get_style()

        y_src = AbstractAdapter.DOUBLE_PADDING * 2 + AbstractAdapter.font_height
        y_sink = y_src
        self.title.set_property('text', self.gst_object.get_name())

        bounds = self.title.get_bounds()
        title_width = bounds.x2 - bounds.x1
        title_height = bounds.y2 - bounds.y1
        pad_width = 0
        for pad in self.gst_object.pads():
            adapter = pad.plugster_adapter
            pad_width = max(pad_width, adapter.get_base_width())
        global_width = max(pad_width * 2 + 6 * AbstractAdapter.DOUBLE_PADDING, title_width + 2 * AbstractAdapter.DOUBLE_PADDING)

        for pad in self.gst_object.pads():
            adapter = pad.plugster_adapter
            self.background_rect.lower(adapter.background)
            adapter.background.lower(self.bounding_rect)
            adapter_width = adapter.get_base_width()
            if pad.get_direction() == gst.PAD_SINK:
                adapter.set_property('x', AbstractAdapter.DOUBLE_PADDING)
                adapter.set_property('y', y_sink + AbstractAdapter.BASE_PADDING)
                adapter.set_background_params(0, y_sink, pad_width + 2 * AbstractAdapter.DOUBLE_PADDING)
                y_sink += AbstractAdapter.font_height + 2 * AbstractAdapter.DOUBLE_PADDING
            else:
                adapter.set_property('x', global_width - AbstractAdapter.DOUBLE_PADDING - adapter_width + PadAdapter.CONNECTOR_RADIUS)
                adapter.set_property('y', y_src + AbstractAdapter.BASE_PADDING)
                adapter.set_background_params(global_width - pad_width -2 * AbstractAdapter.DOUBLE_PADDING, y_src, pad_width + 2 * AbstractAdapter.DOUBLE_PADDING)
                y_src += AbstractAdapter.font_height + 2 * AbstractAdapter.DOUBLE_PADDING

        y_src += AbstractAdapter.BASE_PADDING
        y_sink += AbstractAdapter.BASE_PADDING

        self.title.set_property('width', global_width)
        path = "m {arc_radius} 0 h {small_width} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} {arc_radius} v {height} h -{width} v -{height} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} -{arc_radius}".format(
                    arc_radius = AbstractAdapter.DOUBLE_PADDING,
                    small_width = global_width - 2 * AbstractAdapter.DOUBLE_PADDING,
                    width = global_width,
                    height = title_height)
        self.title_background.set_property('data', path)
        self._update_title_background(self.gst_object.plugster_data)

        self.background_rect.set_property('width', global_width)
        self.background_rect.set_property('height', max(y_src, y_sink))

        self.bounding_rect.set_property('width', global_width)
        self.bounding_rect.set_property('height', max(y_src, y_sink))


    def _update_title_background(self, element_data):
        style = self.get_canvas().get_style()
        if self.is_selected():
            self.title.set_property('fill-color', style.fg[gtk.STATE_SELECTED])
            self.title_background.set_property('fill-color', style.bg[gtk.STATE_SELECTED])
        else:
            self.title.set_property('fill-color', style.fg[gtk.STATE_NORMAL])
            self.title_background.set_property('fill-color', style.dark[gtk.STATE_NORMAL])


    def _on_button_pressed(self, widget, event):
        if event.button == 1: # Left button
            (x, y) = event.get_coords()
            if self.get_canvas().get_items_at(x, y, False) == None:
                self.gst_object.plugster_selection.clear()
        return False


    def _on_start_drag(self, adapter, widget, event):
        if event.button == 1: # Left button
            if event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.BUTTON1_MASK):
                self.get_selection().toggle(self.gst_object)
            else:
                self.get_selection().select(self.gst_object)

            self._on_end_drag_id = adapter.connect('button-release-event', self._on_end_drag)
            self._on_drag_move_id = adapter.connect('motion-notify-event', self._on_drag_move)
            self._drag_x = event.x_root
            self._drag_y = event.y_root
            self._global_dx = 0
            self._global_dy = 0
        return False


    def _on_drag_move(self, adapter, widget, event):
        scale = self.get_canvas().get_scale();
        dx = (event.x_root - self._drag_x) * scale;
        dy = (event.y_root - self._drag_y) * scale;
        self._drag_x = event.x_root;
        self._drag_y = event.y_root;
        self._global_dx += dx;
        self._global_dy += dy;
        adapter.translate(dx, dy);
        return False;


    def _on_end_drag(self, adapter, widget, event):
        adapter.disconnect(self._on_end_drag_id)
        adapter.disconnect(self._on_drag_move_id)
        dx = PipelineCanvas.place_coord_on_grid(self._global_dx)
        dy = PipelineCanvas.place_coord_on_grid(self._global_dy)
        self._drag_x = 0
        self._drag_y = 0
        self._global_dx = 0
        self._global_dy = 0
        adapter.translate(dx, dy)
        adapter.gst_object.plugster_data.x = round(self._global_dx + dx)
        adapter.gst_object.plugster_data.y = round(self._global_dy + dy)
        return False;
