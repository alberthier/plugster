import gobject
import gtk
import gst

from ElementData import *
from PipelineAdapter import *

class PipelineController(gobject.GObject):

    ROOT_PIPELINE_NAME = "plugster_root"


    __gsignals__ = {
        'pipeline-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gst.Pipeline,)),
    }


    def __init__(self, root_widget, canvas):
        gobject.GObject.__init__(self)
        self.root_widget = root_widget
        self.canvas = canvas
        self.filepath = None
        self.root_pipeline = None


    def reset(self):
        self.filepath = None
        self._configure_new_root_pipeline(gst.Pipeline(PipelineController.ROOT_PIPELINE_NAME + "_new"))


    def open(self):
        self.reset()
        self.filepath = self._get_filepath("Open", gtk.FILE_CHOOSER_ACTION_OPEN)
        if self.filepath != None:
            xml = gst.XML()
            xml.connect('object-loaded', ElementData.load)
            error = True
            if xml.parse_file(self.filepath, PipelineController.ROOT_PIPELINE_NAME):
                elements = xml.get_topelements()
                if len(elements) > 0:
                    self._configure_new_root_pipeline(elements[0])
                    error = False
            if error:
                self._display_error_message("Unable to open the file '{0}'".format(self.filepath))
                self.filepath = None


    def close(self):
        self.filepath = None
        self.root_pipeline = None


    def save(self):
        if self.filepath == None:
            self.save_as()
        else:
            error = False
            try:
                output_file = file(self.filepath, 'w')
            except:
                error = True
                output_file = None

            if output_file != None:
                error = gst.xml_write_file(self.root_pipeline, output_file) == -1
                output_file.close()

            if error:
                self._display_error_message("Unable to write the file '{0}'".format(self.filepath))


    def save_as(self):
        path = self._get_filepath("Save", gtk.FILE_CHOOSER_ACTION_SAVE)
        if path != None:
            self.filepath = path
            self.save()


    def _get_filepath(self, text, action):
        if action == gtk.FILE_CHOOSER_ACTION_SAVE:
            icon = gtk.STOCK_SAVE
        else:
            icon = gtk.STOCK_OPEN

        dialog = gtk.FileChooserDialog(text, self.root_widget, action, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, icon, gtk.RESPONSE_ACCEPT))
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
        if isinstance(element, gst.Pipeline):
            self.root_pipeline = element
            ElementData(self.root_pipeline)
            Selection(self.root_pipeline)
            PipelineAdapter(self.root_pipeline, self.canvas)
            self.emit("pipeline-changed", self.root_pipeline)


    def _display_error_message(self, message):
        dialog = gtk.MessageDialog(self.root_widget, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
        dialog.run()
        dialog.destroy()
