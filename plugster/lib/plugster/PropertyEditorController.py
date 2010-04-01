import gtk
import gst

from PropertyEditorModel import *
from CellRendererPropertyName import *
from CellRendererPropertyValue import *

class PropertyEditorController(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)

        self.selection = None
        self.tree_view = gtk.TreeView()
        self.tree_view.props.model = PropertyEditorModel()
        self.tree_view.props.rules_hint = True

        renderer = CellRendererPropertyName(self.tree_view.get_style())
        column = gtk.TreeViewColumn("Property", renderer,
                                    active = PropertyEditorModel.ACTIVE_COLUMN,
                                    markup = PropertyEditorModel.PROPERTY_NAME_COLUMN)
        self.tree_view.append_column(column)

        self.tree_view.set_tooltip_column(PropertyEditorModel.TOOLTIP_COLUMN)

        renderer = CellRendererPropertyValue()
        renderer.connect_object('edited', PropertyEditorModel.set_property_value, self.tree_view.props.model)
        column = gtk.TreeViewColumn("Value", renderer,
                                    active = PropertyEditorModel.ACTIVE_COLUMN,
                                    property_param_spec = PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN,
                                    property_value = PropertyEditorModel.PROPERTY_VALUE_COLUMN)
        self.tree_view.append_column(column)


    def on_pipeline_changed(self, pipeline_controller, new_pipeline):
        selection = new_pipeline.plugster_selection
        selection.connect('selection-changed', self._on_selection_changed)
        self._on_selection_changed(selection)


    def _on_selection_changed(self, selection):
        if selection != None:
            self.tree_view.props.model.set_objects(selection.selected_elements)
