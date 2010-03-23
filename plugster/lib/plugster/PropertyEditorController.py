import gtk
import gst

from PropertyEditorModel import *
from PropertyEditorCellRenderer import *

class PropertyEditorController(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)

        self.selection = None
        self.tree_view = gtk.TreeView()
        self.tree_view.props.model = PropertyEditorModel()
        self.tree_view.props.rules_hint = True

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Property", renderer,
                                    text = PropertyEditorModel.PROPERTY_NAME_COLUMN)
        self.tree_view.append_column(column)

        ##renderer = PropertyEditorCellRenderer()
        ##renderer.connect('edited', self.tree_view.props.model.set_property_value)
        ##column = gtk.TreeViewColumn("Value", renderer,
                                    ##property_param_spec = PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN,
                                    ##property_value = PropertyEditorModel.PROPERTY_VALUE_COLUMN)
        ##self.tree_view.append_column(column)


    def on_pipeline_changed(self, pipeline_controller, new_pipeline):
        selection = new_pipeline.plugster_selection
        selection.connect('selection-changed', self._on_selection_changed)


    def _on_selection_changed(self, selection):
        if selection:
            self.tree_view.props.model.set_objects(selection.selected_elements)