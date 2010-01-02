using Gtk;

namespace Plugster
{

class PropertyEditorModel : GLib.Object, TreeModel
{
    public enum Columns {
        PROPERTY_NAME,
        PROPERTY_PARAM_SPEC,
        PROPERTY_VALUE,
        NB_COLUMNS
    }

    private List<weak GLib.Object> objects;
    private List<weak GLib.ParamSpec> param_specs;

    public PropertyEditorModel()
    {
        param_specs = new List<weak GLib.ParamSpec>();
    }

    public void set_objects(List<weak GLib.Object> objs)
    {
        for (uint index = 0; index < param_specs.length(); ++index) {
            TreePath path = new TreePath.from_indices(index, -1);
            row_deleted(path);
        }

        objects = objs.copy();
        bool first = true;
        param_specs = new List<weak GLib.ParamSpec>();
        foreach (weak GLib.Object object in objects) {
            if (first) {
                first = false;
                foreach (ParamSpec spec in object.get_class().list_properties())
                {
                    param_specs.append(spec);
                }
            } else {
                List<weak GLib.ParamSpec> tmp_param_specs = param_specs.copy();
                foreach (ParamSpec ref_spec in tmp_param_specs) {
                    bool found = false;
                    foreach(ParamSpec spec in object.get_class().list_properties()) {
                        if (spec == ref_spec) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        param_specs.remove(ref_spec);
                    }
                }
            }
        }
        param_specs.sort((CompareFunc) param_spec_cmp);
        int index = 0;
        foreach (ParamSpec spec in param_specs) {
            TreePath path = new TreePath.from_indices(index, -1);
            TreeIter iter = {};
            iter.stamp = index;
            iter.user_data = spec;
            row_inserted(path, iter);
            ++index;
        }
    }

    public void set_property_value(string path, string new_value)
    {
        TreePath tree_path = new TreePath.from_string(path);
        TreeIter iter = {};
        get_iter(out iter, tree_path);
        weak ParamSpec param_spec = ((ParamSpec) iter.user_data);
        string property_name = param_spec.get_name();
        Value property_value = {};

        if (param_spec.value_type.is_a(Type.ENUM)) {
            weak ParamSpecEnum param_spec_enum = (ParamSpecEnum) param_spec;
            weak EnumClass enum_class = param_spec_enum.enum_class;
            for (uint i = 0; i < enum_class.n_values;  ++i) {
                EnumValue* enum_val = &(enum_class.values[i]);
                if (new_value == enum_val->value_name) {
                    property_value.init(typeof(uint));
                    property_value.set_uint(i);
                }
            }
        } else if (param_spec.value_type == typeof(bool)) {
            property_value.init(typeof(bool));
            property_value.set_boolean(new_value == "Yes");
        } else {
            property_value.init(typeof(string));
            property_value.set_string(new_value);
        }

        foreach (GLib.Object object in objects) {
            object.set_property(property_name, property_value);
        }

        row_changed(tree_path, iter);
    }

    public virtual Type get_column_type(int index)
    {
        switch (index)
        {
            case Columns.PROPERTY_NAME:
                return typeof(string);
            case Columns.PROPERTY_PARAM_SPEC:
                return typeof(ParamSpec);
            case Columns.PROPERTY_VALUE:
                return typeof(Value);
            default:
                return Type.INVALID;
        }
    }

    private static int param_spec_cmp(void* a, void* b)
    {
        return ((ParamSpec) a).get_name().collate(((ParamSpec) b).get_name());
    }

    public virtual TreeModelFlags get_flags()
    {
        return TreeModelFlags.ITERS_PERSIST | TreeModelFlags.LIST_ONLY;
    }

    public virtual bool get_iter(out TreeIter iter, TreePath path)
    {
        weak int[] indices = path.get_indices();
        if(indices != null && path.get_depth() == 1) {
            uint i = indices[0];
            if (i < param_specs.length()) {
                iter.stamp = (int) i;
                iter.user_data = param_specs.nth_data(i);
                return true;
            }
        }
        iter.stamp = -1;
        return false;
    }

    public virtual int get_n_columns()
    {
        return Columns.NB_COLUMNS;
    }

    public virtual TreePath get_path(TreeIter iter)
    {
        uint i = (uint) iter.stamp;
        if (i < param_specs.length()) {
            return new TreePath.from_indices(i, -1);
        }
        return new TreePath();
    }

    public virtual void get_value(TreeIter iter, int column, out Value value)
    {
        if ((uint) iter.stamp < param_specs.length()) {
            switch (column) {
                case Columns.PROPERTY_NAME:
                    value.init(typeof(string));
                    value.set_string(((ParamSpec) iter.user_data).get_name());
                    break;
                case Columns.PROPERTY_PARAM_SPEC:
                    value.init(typeof(ParamSpec));
                    value.set_param((ParamSpec) iter.user_data);
                    break;
                case Columns.PROPERTY_VALUE:
                    value.init(typeof(Value));
                    Value prop_val = get_objects_value((ParamSpec) iter.user_data);
                    value.set_boxed(&prop_val);
                    break;
            }
        }
    }

    public virtual bool iter_children(out TreeIter iter, TreeIter? parent)
    {
        if (parent == null && param_specs.length() != 0) {
            iter.stamp = 0;
            iter.user_data = param_specs.nth_data(0);
        }
        iter.stamp = -1;
        return false;
    }

    public virtual bool iter_has_child(TreeIter iter)
    {
        return false;
    }

    public virtual bool iter_next(ref TreeIter iter)
    {
        if (iter.stamp + 1 < (int) param_specs.length()) {
            ++iter.stamp;
            iter.user_data = param_specs.nth_data(iter.stamp);
            return true;
        }
        iter.stamp = -1;
        return false;
    }

    public virtual bool iter_nth_child(out TreeIter iter, TreeIter? parent, int n)
    {
        if (parent == null && n >= 0 && n < param_specs.length()) {
            iter.stamp = n;
            iter.user_data = param_specs.nth_data(n);
            return true;
        }
        iter.stamp = -1;
        return false;
    }

    public virtual int iter_n_children(TreeIter? iter)
    {
        if (iter == null) {
            return (int) param_specs.length();
        }
        return 0;
    }

    public virtual bool iter_parent(out TreeIter iter, TreeIter child)
    {
        iter.stamp = -1;
        return false;
    }

    public virtual void ref_node (TreeIter iter)
    {
    }

    public virtual void unref_node (TreeIter iter)
    {
    }

    private Value get_objects_value(ParamSpec param_spec)
    {
        Value value = {};
        value.init(param_spec.value_type);
        bool first = true;
        foreach(GLib.Object object in objects) {
            if (first) {
                first = false;
                object.get_property(param_spec.get_name(), ref value);
            } else {
                Value tmp_value = {};
                tmp_value.init(param_spec.value_type);
                object.get_property(param_spec.get_name(), ref tmp_value);
                if (param_spec.values_cmp(tmp_value, value) != 0) {
                    value.unset();
                    break;
                }
            }
        }
        return value;
    }
}

}

