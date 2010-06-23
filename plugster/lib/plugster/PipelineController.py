import os.path

import gobject
import gtk
import gst

import Definitions
from ElementData import *
from PipelineAdapter import *
from XmlPipelineDeserializer import *
from XmlPipelineSerializer import *
from AddElementCommand import *
from RemoveElementsCommand import *
from SetPropertyCommand import *
from LinkPadsCommand import *
from UnlinkPadsCommand import *

class PipelineController(gobject.GObject):

    __gsignals__ = {
        'pipeline-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gst.Pipeline,)),
    }


    def __init__(self, root_widget, canvas):
        gobject.GObject.__init__(self)
        self._root_widget = root_widget
        self._canvas = canvas
        self._filepath = None
        self._root_pipeline = None


    def reset(self):
        self._filepath = None
        self._configure_new_root_pipeline(gst.Pipeline(Definitions.ROOT_PIPELINE_NAME + "_new"))


    def open(self):
        self.load(self._get_filepath("Open", gtk.FILE_CHOOSER_ACTION_OPEN))


    def load(self, filepath):
        self.reset()
        if filepath != None:
            data_loader = XmlPipelineDeserializer()
            pipeline = data_loader.load(filepath)
            if pipeline != None:
                self._filepath = filepath
                self._configure_new_root_pipeline(pipeline)
            else:
                self._display_error_message("Unable to open the file '{0}'".format(self._filepath))
                self._filepath = None


    def close(self):
        if self._root_pipeline:
            self._root_pipeline.plugster_selection.clear()
            self._root_pipeline.plugster_adapter.disconnect_signals()
        self._filepath = None
        self._root_pipeline = None


    def save(self):
        if self._filepath == None:
            self.save_as()
        else:
            try:
                serializer = XmlPipelineSerializer(self._root_pipeline)
                serializer.save(self._filepath)
            except Exception as e:
                self._display_error_message("Unable to write the file '{0}'".format(self._filepath))
                self._filepath = None


    def save_as(self):
        path = self._get_filepath("Save", gtk.FILE_CHOOSER_ACTION_SAVE)
        if path != None:
            if not os.path.splitext(path)[1].lower() in [ ".gst", ".xml" ]:
                path += ".gst"
            self._filepath = path
            self.save()


    def _get_filepath(self, text, action):
        if action == gtk.FILE_CHOOSER_ACTION_SAVE:
            icon = gtk.STOCK_SAVE
        else:
            icon = gtk.STOCK_OPEN

        dialog = gtk.FileChooserDialog(text, self._root_widget, action, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, icon, gtk.RESPONSE_ACCEPT))
        dialog.set_select_multiple(False)
        filter = gtk.FileFilter()
        filter.add_mime_type("application/xml")
        dialog.set_filter(filter)
        filename = None
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
        dialog.destroy()
        return filename


    def _configure_new_root_pipeline(self, element):
        if self._root_pipeline:
            self._root_pipeline.plugster_selection.clear()

        if isinstance(element, gst.Pipeline):
            self._root_pipeline = element
            ElementData(self._root_pipeline)
            Selection(self._root_pipeline)
            PipelineAdapter(self._root_pipeline, self._canvas)
            self._root_pipeline.plugster_pipeline_controller = self
            self._root_pipeline.get_bus().add_watch(self._on_bus_message)
            self.emit('pipeline-changed', self._root_pipeline)


    def _display_error_message(self, message):
        dialog = gtk.MessageDialog(self._root_widget, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
        dialog.run()
        dialog.destroy()


    def delete_selection(self):
        self.remove_elements(self._root_pipeline.plugster_selection.selected_elements)


    def add_element(self, factory_name, element_name, x, y):
        self._execute_command(AddElementCommand(self._root_pipeline, factory_name, element_name, x, y))


    def remove_elements(self, elements):
        self._execute_command(RemoveElementsCommand(self._root_pipeline, elements))


    def set_property(self, elements, property_param_spec, property_value):
        self._execute_command(SetPropertyCommand(self._root_pipeline, elements, property_param_spec, property_value))


    def link_pads(self, src_elt_name, src_pad_name, sink_elt_name, sink_pad_name):
        self._execute_command(LinkPadsCommand(self._root_pipeline, src_elt_name, src_pad_name, sink_elt_name, sink_pad_name))


    def unlink_pads(self, src_elt_name, src_pad_name, sink_elt_name, sink_pad_name):
        self._execute_command(UnlinkPadsCommand(self._root_pipeline, src_elt_name, src_pad_name, sink_elt_name, sink_pad_name))


    def _execute_command(self, command):
        self._root_pipeline.set_state(gst.STATE_NULL)
        command.do()
        self._root_pipeline.set_state(gst.STATE_PAUSED)


    def _on_bus_message(self, bus, message):
        if message.type == gst.MESSAGE_STATE_CHANGED:
            self.emit('pipeline-changed', self._root_pipeline)
        return True
