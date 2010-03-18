using Gtk;
using Gdk;

namespace Plugster
{

class PropertyEditorCellRenderer : CellRenderer
{
    public ParamSpec property_param_spec { get; set; }
    public Value property_value { get; set; }

    private HashTable<ParamSpec, CellRenderer> renderers;

    public signal void edited(string path, string new_value);

    construct
    {
        reset();
    }

    public override bool activate(Event event, Widget widget, string path, Rectangle background_area, Rectangle cell_area, CellRendererState flags)
    {
        return get_current_renderer(widget).activate(event, widget, path, background_area, cell_area, flags);
    }

    public override void get_size(Widget widget, Rectangle? cell_area, out int x_offset, out int y_offset, out int width, out int height)
    {
        get_current_renderer(widget).get_size(widget, cell_area, out x_offset, out y_offset, out width, out height);
    }

    public override void render(Gdk.Window window, Widget widget, Rectangle background_area, Rectangle cell_area, Rectangle expose_area, CellRendererState flags)
    {
        get_current_renderer(widget).render(window, widget, background_area, cell_area, expose_area, flags);
    }

    public override weak CellEditable start_editing(Event event, Widget widget, string path, Rectangle background_area, Rectangle cell_area, CellRendererState flags)
    {
        return get_current_renderer(widget).start_editing(event, widget, path, background_area, cell_area, flags);
    }

    public void reset()
    {
        mode = CellRendererMode.EDITABLE;
        renderers = new HashTable<ParamSpec, CellRenderer>.full(GLib.direct_hash, GLib.direct_equal, null, GLib.Object.unref);
    }

    private CellRenderer get_current_renderer(Widget widget)
    {
        CellRenderer renderer = renderers.lookup(property_param_spec);
        bool editable = (property_param_spec.flags & ParamFlags.WRITABLE) == ParamFlags.WRITABLE;
        editable = editable && !((property_param_spec.flags & ParamFlags.CONSTRUCT_ONLY) == ParamFlags.CONSTRUCT_ONLY);

        if (property_param_spec.value_type == typeof(char)) {
            if (renderer == null) {
                weak ParamSpecChar spec = (ParamSpecChar) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(uchar)) {
            if (renderer == null) {
                weak ParamSpecUChar spec = (ParamSpecUChar) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(int)) {
            if (renderer == null) {
                weak ParamSpecInt spec = (ParamSpecInt) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(uint)) {
            if (renderer == null) {
                weak ParamSpecUInt spec = (ParamSpecUInt) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(long)) {
            if (renderer == null) {
                weak ParamSpecLong spec = (ParamSpecLong) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(ulong)) {
            if (renderer == null) {
                weak ParamSpecULong spec = (ParamSpecULong) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(int64)) {
            if (renderer == null) {
                weak ParamSpecInt64 spec = (ParamSpecInt64) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(uint64)) {
            if (renderer == null) {
                weak ParamSpecUInt64 spec = (ParamSpecUInt64) property_param_spec;
                renderer = create_renderer_spin(widget, 0, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(float)) {
            if (renderer == null) {
                weak ParamSpecFloat spec = (ParamSpecFloat) property_param_spec;
                renderer = create_renderer_spin(widget, 2, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(double)) {
            if (renderer == null) {
                weak ParamSpecDouble spec = (ParamSpecDouble) property_param_spec;
                renderer = create_renderer_spin(widget, 2, editable, spec.minimum, spec.maximum);
            }
            update_renderer_spin_value((CellRendererSpin) renderer);
        } else if (property_param_spec.value_type == typeof(bool)) {
            if (renderer == null) {
                renderer = create_renderer_bool(widget, editable);
            }
            update_renderer_bool_value((CellRendererCombo) renderer);
        } else if (property_param_spec.value_type == typeof(string)) {
            if (renderer == null) {
                renderer = create_renderer_text(widget, editable);
            }
            update_renderer_text_value((CellRendererText) renderer);
        } else if (property_param_spec.value_type.is_a(Type.ENUM) && editable) {
            weak ParamSpecEnum spec = (ParamSpecEnum) property_param_spec;
            if (renderer == null) {
                renderer = create_renderer_combo(widget, spec.enum_class);
            }
            update_renderer_combo_value((CellRendererCombo) renderer, spec.enum_class);
        } else {
            if (renderer == null) {
                renderer = create_renderer_text(widget, false);
            }
            update_renderer_text_value((CellRendererText) renderer);
        }
        renderers.insert(property_param_spec, renderer);

        return renderer;
    }

    private CellRenderer create_renderer_spin(Widget widget, uint digits, bool editable, double lower, double upper)
    {
        CellRendererSpin renderer = new CellRendererSpin();
        renderer.edited += on_renderer_value_changed;
        if (!editable) {
            renderer.foreground = widget.get_style().text[Gtk.StateType.INSENSITIVE].to_string();
        } else {
            renderer.foreground = widget.get_style().text[Gtk.StateType.NORMAL].to_string();
        }
        renderer.adjustment = new Adjustment(0.0, lower, upper, 1.0, 10.0, 0.0);
        renderer.digits = digits;
        renderer.editable = editable;
        return renderer;
    }

    private void update_renderer_spin_value(CellRendererSpin renderer)
    {
        update_renderer_text_value(renderer);
    }

    private CellRenderer create_renderer_bool(Widget widget, bool editable)
    {
        CellRendererCombo renderer = new CellRendererCombo();
        renderer.edited += on_renderer_value_changed;
        if (!editable) {
            renderer.foreground = widget.get_style().text[Gtk.StateType.INSENSITIVE].to_string();
        } else {
            renderer.foreground = widget.get_style().text[Gtk.StateType.NORMAL].to_string();
        }
        ListStore store = new ListStore(1, typeof(string));
        renderer.text_column = 0;
        renderer.has_entry = false;
        renderer.editable = true;

        TreeIter iter = {};
        store.append(out iter);
        store.set(iter, 0, "Yes", -1);
        store.append(out iter);
        store.set(iter, 0, "No", -1);

        renderer.model = store;
        return renderer;
    }

    private void update_renderer_bool_value(CellRendererCombo renderer)
    {
        if (property_value.type() != Type.INVALID) {
            Value val = {};
            val.init(typeof(bool));
            if (property_value.transform(ref val)) {
                if (val.get_boolean()) {
                    renderer.text = "Yes";
                } else {
                    renderer.text = "No";
                }
            } else {
                    renderer.text = "---";
            }
        } else {
            renderer.text = "---";
        }
    }

    private CellRenderer create_renderer_combo(Widget widget, EnumClass enum_class)
    {
        CellRendererCombo renderer = new CellRendererCombo();
        renderer.edited += on_renderer_value_changed;
        ListStore store = new ListStore(1, typeof(string));
        renderer.model = store;
        renderer.text_column = 0;
        renderer.has_entry = false;
        renderer.editable = true;
        TreeIter iter = {};

        for (uint i = 0; i < enum_class.n_values;  ++i) {
            store.append(out iter);
            EnumValue* enum_val = enum_class.values;
            enum_val += i;
            store.set(iter, 0, enum_val->value_name, -1);
        }
        return renderer;
    }

    private void update_renderer_combo_value(CellRendererCombo renderer, EnumClass enum_class)
    {
        int index = -1;
        if (property_value.type() != Type.INVALID) {
            Value val = {};
            val.init(typeof(int));
            if (property_value.transform(ref val)) {
                index = val.get_int();
            }
        }

        if (index >= 0 && index < enum_class.n_values) {
            EnumValue* enum_val = enum_class.values;
            enum_val += index;
            renderer.text = enum_val->value_name;
        } else {
            renderer.text = "---";
        }
    }

    private CellRenderer create_renderer_text(Widget widget, bool editable)
    {
        CellRendererText renderer = new CellRendererText();
        renderer.edited += on_renderer_value_changed;
        if (!editable) {
            renderer.foreground = widget.get_style().text[Gtk.StateType.INSENSITIVE].to_string();
        } else {
            renderer.foreground = widget.get_style().text[Gtk.StateType.NORMAL].to_string();
        }
        renderer.editable = editable;
        return renderer;
    }

    private void update_renderer_text_value(CellRendererText renderer)
    {
        if (property_value.type() != Type.INVALID) {
            Value val = {};
            val.init(typeof(string));
            if (property_value.transform(ref val)) {
                renderer.text = val.get_string();
            } else {
                renderer.text = "---";
            }
        } else {
            renderer.text = "---";
        }
    }

    private void on_renderer_value_changed(string path, string new_text)
    {
        edited(path, new_text);
    }
}

}
