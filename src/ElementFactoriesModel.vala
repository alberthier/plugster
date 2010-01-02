using Gtk;
using Gst;

namespace Plugster
{

class ElementFactoriesModel : TreeStore
{
    public enum Columns {
        NAME,
        ELEMENT_FACTORY_POINTER,
        ICON,
        NB_COLUMNS
    }

    construct
    {
        GLib.Type[] types = new GLib.Type[Columns.NB_COLUMNS];
        types[Columns.NAME] = typeof(string);
        types[Columns.ELEMENT_FACTORY_POINTER] = typeof(ElementFactory);
        types[Columns.ICON] = typeof(string);
        set_column_types(types);

        var registry = Registry.get_default();
        var element_factories = registry.get_feature_list(typeof(ElementFactory));

        foreach (PluginFeature feature in element_factories) {
            ElementFactory factory = (ElementFactory) feature;
            TreeIter current;
            TreeIter parent;
            bool parent_valid = get_parent_iter(factory.get_klass().split("/"), out parent);
            if (parent_valid) {
                append(out current, parent);
            } else {
                append(out current, null);
            }
            set(current,
                Columns.NAME, factory.get_longname(),
                Columns.ELEMENT_FACTORY_POINTER, factory,
                Columns.ICON, STOCK_CONNECT,
                -1);
        }
    }

    private bool get_parent_iter(string[] klass, out TreeIter parent)
    {
        bool parent_valid = false;
        foreach (string section in klass) {
            TreeIter current = {};

            bool valid = false;
            if (!parent_valid) {
                valid = iter_children(out current, null);
            } else {
                valid = iter_children(out current, parent);
            }

            while (valid) {
                string text;
                get(current, Columns.NAME, out text, -1);
                if (section == text) {
                    break;
                } else {
                    valid = iter_next(ref current);
                }
            }

            if (!valid) {
                if (parent_valid) {
                    append(out current, parent);
                } else {
                    append(out current, null);
                }
                set(current, Columns.NAME, section, Columns.ICON, STOCK_DIRECTORY, -1);
            }

            parent = current;
            parent_valid = true;
        }

        return parent_valid;
    }
}

}

