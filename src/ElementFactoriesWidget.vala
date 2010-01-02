using Gtk;
using Gst;

namespace Plugster
{

class ElementFactoriesWidget : TreeView
{

    public const TargetEntry[] drag_targets = {
        { "application/x-plugster-element-factory", 0, 0}
    };

    construct
    {
        width_request = 230;

        var column = new TreeViewColumn();
        column.set_title("Element");

        var icon_renderer = new CellRendererPixbuf();
        icon_renderer.icon_name = "gtk-open";
        column.pack_start(icon_renderer, false);
        column.add_attribute(icon_renderer, "icon-name", ElementFactoriesModel.Columns.ICON);

        var renderer = new CellRendererText();
        column.pack_start(renderer, true);
        column.add_attribute(renderer, "text", ElementFactoriesModel.Columns.NAME);

        append_column(column);
        enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, drag_targets, Gdk.DragAction.COPY);
        set_model(new ElementFactoriesModel());

        drag_data_get += drag_data_get_element_factory;
    }

    private void drag_data_get_element_factory(Gdk.DragContext context, Gtk.SelectionData selection_data, uint info, uint time)
    {
        TreeModel model = null;
        TreeIter iter;
        if (get_selection().get_selected(out model, out iter)) {
            if (!model.iter_has_child(iter)) {
                ElementFactory factory = null;
                model.get(iter, ElementFactoriesModel.Columns.ELEMENT_FACTORY_POINTER, out factory, -1);
                Gdk.Atom atom = Gdk.Atom.intern("application/x-plugster-element-factory", true);
                string factory_name = factory.get_name();
                uchar[] data = new uchar[factory_name.size() + 1];
                GLib.Memory.copy(data, factory_name, factory_name.size() + 1);
                selection_data.set(atom, 8, data);
            }
        }
    }
}

}

