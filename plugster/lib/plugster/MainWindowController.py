import traceback

import gobject
import gtk

from ElementFactoriesWidget import *
from PipelineController import *
from PipelineCanvas import *
from PropertyEditorController import *

class MainWindowController(gobject.GObject):

    def __init__(self, path):
        gobject.GObject.__init__(self)
        self.window = None
        self.pipeline_controller = None
        self.property_editor_controller = None

        builder = gtk.Builder()
        try:
            if builder.add_from_file(path + "/share/plugster/mainwindow.ui") > 0:
                mainwindow = builder.get_object("mainwindow")
                mainwindow.connect("destroy", self.quit_app)

                elements_widget_container = builder.get_object("elements_widget_container")
                pipeline_canvas_scrollwindow = builder.get_object("pipeline_canvas_scrollwindow")
                property_editor_scrollwindow = builder.get_object("property_editor_scrollwindow")

                elements_widget_container.add(ElementFactoriesWidget())
                canvas = PipelineCanvas()
                pipeline_canvas_scrollwindow.add(canvas)

                self.pipeline_controller = PipelineController(mainwindow, canvas)
                self.property_editor_controller = PropertyEditorController()
                property_editor_scrollwindow.add(self.property_editor_controller.tree_view)
                self.pipeline_controller.connect('pipeline-changed', self.property_editor_controller.on_pipeline_changed)

                action = builder.get_object("action_new")
                action.connect_object('activate', PipelineController.reset, self.pipeline_controller)

                action = builder.get_object("action_open")
                action.connect_object('activate', PipelineController.open, self.pipeline_controller)

                action = builder.get_object("action_save")
                action.connect_object('activate', PipelineController.save, self.pipeline_controller)

                action = builder.get_object("action_save_as")
                action.connect_object('activate', PipelineController.save_as, self.pipeline_controller)

                action = builder.get_object("action_quit")
                action.connect('activate', self.quit_app)

                action = builder.get_object("action_undo")
                action.connect('activate', self.undo)

                action = builder.get_object("action_redo")
                action.connect('activate', self.redo)

                action = builder.get_object("action_cut")
                action.connect('activate', self.cut)

                action = builder.get_object("action_copy")
                action.connect('activate', self.copy)

                action = builder.get_object("action_paste")
                action.connect('activate', self.paste)

                action = builder.get_object("action_delete")
                action.connect('activate', self.delete)

                action = builder.get_object("action_about")
                action.connect('activate', self.about)

                mainwindow.show_all()

                self.pipeline_controller.reset()
            else:
                print("Error loading the ui file")
                gtk.main_quit()

        except Exception as err:
            traceback.print_exc()
            gtk.main_quit()


    def load(self, filepath):
        self.pipeline_controller.load(filepath)


    def quit_app(self, object):
        self.pipeline_controller.close()
        gtk.main_quit()


    def undo(self, object):
        print("undo")


    def redo(self, object):
        print("redo")


    def cut(self, object):
        print("cut")


    def copy(self, object):
        print("copy")


    def paste(self, object):
        print("paste")


    def delete(self, object):
        print("delete")


    def about(self, object):
        print("about")

