using Gtk;

namespace Plugster
{

class PropertyEditorController : GLib.Object
{
    public TreeView tree_view { get; set; }

    private GLib.Object tmp;

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

        var objects = new List<weak GLib.Object>();
        tmp = Gst.ElementFactory.make("tee", "tee1");
        objects.append(tmp);
        model.set_objects(objects);
    }
}

}

