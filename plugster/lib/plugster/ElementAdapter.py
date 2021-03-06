import glib
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

        self._on_end_drag_id = None
        self._on_drag_move_id = None
        self._drag_x = 0
        self._drag_y = 0
        self._global_dx = 0
        self._global_dy = 0

        factory = self.gst_object.get_factory()
        self.props.tooltip = "<b>{0}</b>\n{1}".format(glib.markup_escape_text(factory.get_longname()), glib.markup_escape_text(factory.get_description()))

        self.gst_object.connect('pad-added', self._thread_safe_on_pad_added)
        self.gst_object.connect('pad-removed', self._thread_safe_on_pad_removed)
        self.gst_object.connect('no-more-pads', self._thread_safe_relayout)
        self.connect('button-press-event', self._on_start_drag)

        data = self.gst_object.plugster_data
        data.connect('selected-state-changed', self._update_title_background)
        style = self.get_canvas().get_style()
        font_desc = self.props.font_desc
        font_desc.set_weight(pango.WEIGHT_BOLD)

        self._background_rect = goocanvas.Rect(parent = self,
                                               fill_color = style.bg[gtk.STATE_NORMAL],
                                               line_width = 0.0,
                                               radius_x = AbstractAdapter.DOUBLE_PADDING,
                                               radius_y = AbstractAdapter.DOUBLE_PADDING)
        self._title_background = goocanvas.Path(parent = self,
                                                data = "m 0 0",
                                                line_width = 0.0)
        self._title = goocanvas.Text(parent = self,
                                     font_desc = font_desc,
                                     y = AbstractAdapter.BASE_PADDING,
                                     alignment = pango.ALIGN_CENTER)
        self._bounding_rect = goocanvas.Rect(parent = self,
                                             stroke_color = style.dark[gtk.STATE_NORMAL],
                                             line_width = 2.0,
                                             radius_x = AbstractAdapter.DOUBLE_PADDING,
                                             radius_y = AbstractAdapter.DOUBLE_PADDING)

        for pad in self.gst_object.pads():
            self._on_pad_added(self.gst_object, pad)

        self._relayout(self.gst_object)
        self.translate(data.x, data.y)



    def _thread_safe_on_pad_added(self, element, pad):
        glib.idle_add(self._on_pad_added, element, pad)


    def _thread_safe_on_pad_removed(self, element, pad):
        glib.idle_add(self._on_pad_removed, element, pad)


    def _thread_safe_relayout(self, element):
        glib.idle_add(self._relayout, element)


    def _on_pad_added(self, element, pad):
        PadAdapter(pad, self)


    def _on_pad_removed(self, element, pad):
        pad.plugster_adapter.remove()


    def _relayout(self, element):
        style = self.get_canvas().get_style()

        y_src = AbstractAdapter.DOUBLE_PADDING * 2 + AbstractAdapter.font_height
        y_sink = y_src
        self._title.props.text = self.gst_object.get_name()

        bounds = self._title.get_bounds()
        title_width = bounds.x2 - bounds.x1
        title_height = bounds.y2 - bounds.y1
        pad_width = 0
        for pad in self.gst_object.pads():
            adapter = pad.plugster_adapter
            pad_width = max(pad_width, adapter.get_base_width())
        global_width = max(pad_width * 2 + 6 * AbstractAdapter.DOUBLE_PADDING, title_width + 2 * AbstractAdapter.DOUBLE_PADDING)

        for pad in self.gst_object.pads():
            adapter = pad.plugster_adapter
            adapter.lower(self._bounding_rect)
            adapter_width = adapter.get_base_width()
            adapter.set_background_width(pad_width + 2 * AbstractAdapter.DOUBLE_PADDING)
            if pad.get_direction() == gst.PAD_SINK:
                adapter.props.x = AbstractAdapter.DOUBLE_PADDING
                adapter.props.y = y_sink + AbstractAdapter.BASE_PADDING
                y_sink += AbstractAdapter.font_height + 2 * AbstractAdapter.DOUBLE_PADDING
            else:
                adapter.props.x = global_width - AbstractAdapter.DOUBLE_PADDING - adapter_width + PadAdapter.CONNECTOR_RADIUS
                adapter.props.y = y_src + AbstractAdapter.BASE_PADDING
                y_src += AbstractAdapter.font_height + 2 * AbstractAdapter.DOUBLE_PADDING

        y_src += AbstractAdapter.BASE_PADDING
        y_sink += AbstractAdapter.BASE_PADDING

        self._title.props.width = global_width
        path = "m {arc_radius} 0 h {small_width} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} {arc_radius} v {height} h -{width} v -{height} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} -{arc_radius}".format(
                    arc_radius = AbstractAdapter.DOUBLE_PADDING,
                    small_width = global_width - 2 * AbstractAdapter.DOUBLE_PADDING,
                    width = global_width,
                    height = title_height)
        self._title_background.props.data = path
        self._update_title_background(self.gst_object.plugster_data)

        self._background_rect.props.width = global_width
        self._background_rect.props.height = max(y_src, y_sink)

        self._bounding_rect.props.width = global_width
        self._bounding_rect.props.height = max(y_src, y_sink)


    def _update_title_background(self, element_data):
        style = self.get_canvas().get_style()
        if self.is_selected():
            self._title.props.fill_color = style.fg[gtk.STATE_SELECTED]
            self._title_background.props.fill_color = style.bg[gtk.STATE_SELECTED]
        else:
            self._title.props.fill_color = style.fg[gtk.STATE_NORMAL]
            self._title_background.props.fill_color = style.dark[gtk.STATE_NORMAL]


    def _on_start_drag(self, adapter, widget, event):
        if self._on_end_drag_id == None and self._on_drag_move_id == None:
            if event.button == 1: # Left button
                if event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.BUTTON1_MASK):
                    self.get_selection().toggle(self.gst_object)
                else:
                    self.get_selection().select(self.gst_object)
                    self.raise_(None)

                self._on_end_drag_id = adapter.connect('button-release-event', self._on_end_drag)
                self._on_drag_move_id = adapter.connect('motion-notify-event', self._on_drag_move)
                self._drag_x = event.x_root
                self._drag_y = event.y_root
                self._global_dx = 0
                self._global_dy = 0
        return False


    def _on_drag_move(self, adapter, widget, event):
        scale = self.get_canvas().get_scale()
        dx = (event.x_root - self._drag_x) * scale
        dy = (event.y_root - self._drag_y) * scale
        self._drag_x = event.x_root
        self._drag_y = event.y_root
        self._global_dx += dx
        self._global_dy += dy
        self._update_position(dx, dy)
        return False


    def _on_end_drag(self, adapter, widget, event):
        adapter.disconnect(self._on_end_drag_id)
        adapter.disconnect(self._on_drag_move_id)
        self._on_end_drag_id = None
        self._on_drag_move_id = None

        scale = self.get_canvas().get_scale()
        self._global_dx += (event.x_root - self._drag_x) * scale
        self._global_dy += (event.y_root - self._drag_y) * scale
        dx = PipelineCanvas.place_coord_on_grid(self._global_dx)
        dy = PipelineCanvas.place_coord_on_grid(self._global_dy)
        self._update_position(dx, dy)
        adapter.gst_object.plugster_data.x += round(self._global_dx + dx)
        adapter.gst_object.plugster_data.y += round(self._global_dy + dy)

        self._drag_x = 0
        self._drag_y = 0
        self._global_dx = 0
        self._global_dy = 0
        return False


    def _update_position(self, dx, dy):
        self.translate(dx, dy)
        self.ensure_updated()
        for pad in self.gst_object.pads():
            pad.plugster_adapter.update_link()
