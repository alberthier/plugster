import glib
import pango
import gtk
import gst

class ElementDetailsController(object):

    def __init__(self, view):
        object.__init__(self)

        self.buffer = gtk.TextBuffer()
        view.set_buffer(self.buffer)
        font_size = view.get_pango_context().get_font_description().get_size()

        self._title1 = gtk.TextTag("title1")
        self._title1.props.size = int(1.5 * font_size)
        self._title1.props.weight = pango.WEIGHT_BOLD
        self.buffer.get_tag_table().add(self._title1)

        self._title2 = gtk.TextTag("title2")
        self._title2.props.size = int(1.25 * font_size)
        self._title2.props.weight = pango.WEIGHT_BOLD
        self.buffer.get_tag_table().add(self._title2)

        self._bold = gtk.TextTag("bold")
        self._bold.props.weight = pango.WEIGHT_BOLD
        self.buffer.get_tag_table().add(self._bold)


    def on_pipeline_changed(self, sender, pipeline):
        pipeline.plugster_selection.connect('selection-changed', self._on_selection_changed)


    def _on_selection_changed(self, selection):
        self.buffer.delete(self.buffer.get_start_iter(), self.buffer.get_end_iter())
        if len(selection.selected_elements) == 1:
            element = selection.selected_elements[0]
            factory = element.get_factory()
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), factory.get_longname(), self._title1)
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert(self.buffer.get_end_iter(), factory.get_description())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Author: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.get_author())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Rank: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), str(factory.get_rank()))
            if factory.get_rank() in gst.Rank.__enum_values__:
                text = gst.Rank.__enum_values__[factory.get_rank()].value_nick
                self.buffer.insert(self.buffer.get_end_iter(), " (" + text + ")")
            self.buffer.insert(self.buffer.get_end_iter(), "\n\n")

            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Plugin: " + factory.plugin.get_name(), self._title2)
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_description())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Filename: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_filename())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Version: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_version())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "License: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_license())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Source module: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_source())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Binary package: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_package())
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Origin URL: ", self._bold)
            self.buffer.insert(self.buffer.get_end_iter(), factory.plugin.get_origin())
            self.buffer.insert(self.buffer.get_end_iter(), "\n\n")

            self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Pad templates:", self._title2)
            self.buffer.insert(self.buffer.get_end_iter(), "\n")
            for template in element.get_pad_template_list():
                if template.direction == gst.PAD_SINK:
                    template_dir = "SINK template: "
                else:
                    template_dir = "SRC template: "
                self.buffer.insert_with_tags(self.buffer.get_end_iter(), template_dir, self._bold)
                self.buffer.insert(self.buffer.get_end_iter(), template.name_template)
                self.buffer.insert(self.buffer.get_end_iter(), "\n")
                self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Availability: ", self._bold)
                self.buffer.insert(self.buffer.get_end_iter(), template.presence.value_nick)
                self.buffer.insert(self.buffer.get_end_iter(), "\n")
                self.buffer.insert_with_tags(self.buffer.get_end_iter(), "Capabilities:", self._bold)
                for structure in template.get_caps():
                    self.buffer.insert(self.buffer.get_end_iter(), u"\n    \u2022 " + glib.markup_escape_text(structure.get_name()))
                    for i in xrange(structure.n_fields()):
                        name = structure.nth_field_name(i)
                        val = self._get_structure_value_string(structure[name])
                        self.buffer.insert(self.buffer.get_end_iter(), u"\n        \u2022 {0} = {1}".format(glib.markup_escape_text(name), glib.markup_escape_text(val)))
                self.buffer.insert(self.buffer.get_end_iter(), "\n\n")


    def _get_structure_value_string(self, value):
        result = None
        if isinstance(value, gst.Fourcc):
            result = value.fourcc
        elif isinstance(value, gst.IntRange) or isinstance(value, gst.DoubleRange):
            result = "[ {0}, {1} ]".format(value.low, value.high)
        elif isinstance(value, gst.FractionRange):
            result = "[ {0}/{1}, {2}/{3} ]".format(value.low.num, value.low.denom, value.high.num, value.high.denom)
        elif isinstance(value, gst.Fraction):
            result = "[ {0}/{1} ]".format(value.num, value.denom)
        elif isinstance(value, list):
            result = "{ "
            for index, v in enumerate(value):
                if index != 0:
                    result += ", "
                result += self._get_structure_value_string(v)
            result += " }"
        else:
            result = str(value)
        return glib.markup_escape_text(result)
