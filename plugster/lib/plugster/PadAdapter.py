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

        style = self.get_canvas().get_style()

        self.background = goocanvas.Path(parent = elt_adapter,
                                         data = "m 0 0",
                                         line_width = 0.0)
        self.background.lower(self)

        title = goocanvas.Text(parent = self,
                               text = self.gst_object.get_name())
        connector = goocanvas.Ellipse(parent = self,
                                      radius_x = PadAdapter.CONNECTOR_RADIUS,
                                      radius_y = PadAdapter.CONNECTOR_RADIUS,
                                      fill_color = self._get_connector_color(),
                                      line_width = 2.0,
                                      stroke_color = style.dark[gtk.STATE_NORMAL])

        if self.gst_object.get_direction() == gst.PAD_SINK:
            self.background.set_property('fill-color', PadAdapter.SINK_COLOR)
            title.translate(PadAdapter.CONNECTOR_RADIUS / 2 + AbstractAdapter.DOUBLE_PADDING, 0.0)
            connector.translate(0.0, AbstractAdapter.font_height / 2)
        else:
            self.background.set_property('fill-color', PadAdapter.SRC_COLOR)
            bounds = title.get_bounds()
            connector.translate(bounds.x2 - bounds.x1 + PadAdapter.CONNECTOR_RADIUS / 2 + AbstractAdapter.DOUBLE_PADDING, AbstractAdapter.font_height / 2)

        tooltip = "<b>Capabilities</b>"
        for structure in self.gst_object.get_caps():
            tooltip += u"\n    \u2022 " + structure.get_name()
            i = 0
            while i < structure.n_fields():
                name = structure.nth_field_name(i)
                val = self._get_structure_value_string(structure[name])
                tooltip += u"\n        \u2022 {0} = {1}".format(name, val)
                i += 1

        self.set_property('tooltip', tooltip)
        self.background.set_property('tooltip', tooltip)



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
        self.background.set_property('data', path)


    def get_base_width(self):
        bounds = self.get_bounds()
        return bounds.x2 - bounds.x1


    def _get_connector_color(self):
        if self.gst_object.is_linked():
            return Definitions.PadAdapter.LINKED_COLOR
        else:
            style = self.get_canvas().get_style();
            return style.bg[gtk.STATE_NORMAL]


    def _get_structure_value_string(self, value):
        if isinstance(value, gst.Fourcc):
            return value.fourcc
        elif isinstance(value, gst.IntRange) or isinstance(value, gst.DoubleRange):
            return "[ {0}, {1} ]".format(value.low, value.high)
        elif isinstance(value, gst.FractionRange):
            return "[ {0}/{1}, {2}/{3} ]".format(value.low.num, value.low.denom, value.high.num, value.high.denom)
        elif isinstance(value, gst.Fraction):
            return "[ {0}/{1} ]".format(value.num, value.denom)
        elif isinstance(value, list):
            val_str = "{ "
            first = True
            for v in value:
                if first:
                    first = False
                else:
                    val_str += ", "
                val_str += self._get_structure_value_string(v)
            val_str += " }"
            return val_str
        else:
            return str(value)
