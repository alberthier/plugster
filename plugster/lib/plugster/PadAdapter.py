import glib
import cairo
import gtk
import goocanvas

from AbstractAdapter import *

class PadAdapter(AbstractAdapter):

    CONNECTOR_RADIUS = 5.0
    SINK_COLOR       = "#73d216"
    SRC_COLOR        = "#f57900"
    LINKED_COLOR     = "#204a87"

    def __init__(self, gst_pad, elt_adapter):
        AbstractAdapter.__init__(self, gst_pad, elt_adapter)

        self._on_end_drag_id = None
        self._on_drag_move_id = None
        self._link = None

        style = self.get_canvas().get_style()

        self.background = goocanvas.Path(parent = elt_adapter,
                                         data = "m 0 0",
                                         line_width = 0.0)
        self.background.lower(self)

        title = goocanvas.Text(parent = self,
                               text = self.gst_object.get_name())
        self._connector = goocanvas.Ellipse(parent = self,
                                           radius_x = PadAdapter.CONNECTOR_RADIUS,
                                           radius_y = PadAdapter.CONNECTOR_RADIUS,
                                           fill_color = self._get_connector_color(),
                                           line_width = 2.0,
                                           stroke_color = style.dark[gtk.STATE_NORMAL])

        self.background.connect('button-press-event', self._on_start_drag)
        self.connect('button-press-event', self._on_start_drag)

        if self.gst_object.get_direction() == gst.PAD_SINK:
            self.background.props.fill_color = PadAdapter.SINK_COLOR
            title.translate(PadAdapter.CONNECTOR_RADIUS / 2 + AbstractAdapter.DOUBLE_PADDING, 0.0)
            self._connector.translate(0.0, AbstractAdapter.font_height / 2)
        else:
            self.background.props.fill_color = PadAdapter.SRC_COLOR
            bounds = title.get_bounds()
            self._connector.translate(bounds.x2 - bounds.x1 + PadAdapter.CONNECTOR_RADIUS / 2 + AbstractAdapter.DOUBLE_PADDING, AbstractAdapter.font_height / 2)

        tooltip = "<b>Capabilities</b>"
        for structure in self.gst_object.get_caps():
            tooltip += u"\n    \u2022 " + glib.markup_escape_text(structure.get_name())

        self.props.tooltip = tooltip
        self.background.props.tooltip = tooltip



    def set_background_params(self, x, y, width):
        if self.gst_object.get_direction() == gst.PAD_SINK:
            path_tpl = "m {x} {y} h {width} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} {arc_radius} v {small_height} a {arc_radius} {arc_radius} 0 0 1 -{arc_radius} {arc_radius} h -{width} v -{height}"
        else:
            x += AbstractAdapter.BASE_PADDING
            path_tpl = "m {x} {y} h {width} v {height} h -{width} a {arc_radius} {arc_radius} 0 0 1 -{arc_radius} -{arc_radius} v -{small_height} a {arc_radius} {arc_radius} 0 0 1 {arc_radius} -{arc_radius}"

        path = path_tpl.format(x = x,
                               y = y,
                               arc_radius = AbstractAdapter.BASE_PADDING,
                               width = width - AbstractAdapter.BASE_PADDING,
                               height = AbstractAdapter.font_height + AbstractAdapter.DOUBLE_PADDING,
                               small_height = AbstractAdapter.font_height)
        self.background.props.data = path


    def get_base_width(self):
        bounds = self.get_bounds()
        return bounds.x2 - bounds.x1


    def _get_connector_color(self):
        if self.gst_object.is_linked():
            return Definitions.PadAdapter.LINKED_COLOR
        else:
            style = self.get_canvas().get_style()
            return style.bg[gtk.STATE_NORMAL]


    def _on_start_drag(self, adapter, widget, event):
        if self._on_end_drag_id == None and self._on_drag_move_id == None:
            bounds = self._connector.get_bounds()
            x = bounds.x1 + PadAdapter.CONNECTOR_RADIUS + 1.0
            y = bounds.y1 + PadAdapter.CONNECTOR_RADIUS + 1.0
            points = goocanvas.Points([(x, y), (event.x_root, event.y_root)])
            parent = self.gst_object.get_parent_element().plugster_data.get_pipeline().plugster_adapter.links_layer
            self._link = goocanvas.Polyline(parent = parent,
                                            points = points,
                                            line_width = 4,
                                            stroke_color = PadAdapter.LINKED_COLOR,
                                            line_cap = cairo.LINE_CAP_ROUND)
            self._on_end_drag_id = adapter.connect('button-release-event', self._on_end_drag)
            self._on_drag_move_id = adapter.connect('motion-notify-event', self._on_drag_move)
        return True


    def _on_drag_move(self, adapter, widget, event):
        bounds = self._connector.get_bounds()
        x = bounds.x1 + PadAdapter.CONNECTOR_RADIUS + 1.0
        y = bounds.y1 + PadAdapter.CONNECTOR_RADIUS + 1.0
        points = goocanvas.Points([(x, y), (event.x_root, event.y_root)])
        self._link.props.points = points
        pad_adapter = self._get_pad_adapter_at(event.x_root, event.y_root)
        cursor = None
        if pad_adapter != None:
            # Hack to get the real pad instance and not the weakproxy
            pad = pad_adapter.gst_object.get_parent_element().get_pad(pad_adapter.gst_object.get_name())
            if not self.gst_object.can_link(pad):
                cursor = gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
        self.get_canvas().props.window.set_cursor(cursor)
        return True


    def _on_end_drag(self, adapter, widget, event):
        self.get_canvas().props.window.set_cursor(None)
        adapter.disconnect(self._on_end_drag_id)
        adapter.disconnect(self._on_drag_move_id)
        self._on_end_drag_id = None
        self._on_drag_move_id = None
        self._link.remove()
        self._link = None
        return True


    def _get_pad_adapter_at(self, x, y):
        items = self.get_canvas().get_items_at(x, y, False)
        for item in items:
            p = item
            while p != None:
                if isinstance(p, PadAdapter) and p != self:
                    return p
                p = p.get_parent()
        return None
