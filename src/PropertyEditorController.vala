using Gtk;
using Gst;

namespace Plugster
{

class PropertyEditorController : GLib.Object
{
    public TreeView tree_view { get; set; }
    private Selection? selection;

    public PropertyEditorController()
    {
        tree_view = new TreeView();
        var model = new PropertyEditorModel();
        tree_view.model = model;
        tree_view.rules_hint = true;

        var renderer_text = new CellRendererText();
        var column = new TreeViewColumn.with_attributes("Property", renderer_text, "text", PropertyEditorModel.Columns.PROPERTY_NAME, null);
        tree_view.append_column(column);

        var renderer_property = new PropertyEditorCellRenderer();
        renderer_property.edited += model.set_property_value;
        column = new TreeViewColumn.with_attributes("Value", renderer_property,
                                                    "property_param_spec", PropertyEditorModel.Columns.PROPERTY_PARAM_SPEC,
                                                    "property_value", PropertyEditorModel.Columns.PROPERTY_VALUE,
                                                    null);
        tree_view.append_column(column);
    }

    public void on_pipeline_changed(Pipeline new_pipeline)
    {
        selection = Selection.get_selection(new_pipeline);
        selection.selection_changed += on_selection_changed;
    }

    public void on_selection_changed()
    {
        if (selection != null) {
            ((PropertyEditorModel) tree_view.model).set_objects(selection.get_selected_elements());
        }
    }
}

}

