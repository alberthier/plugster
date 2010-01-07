using Gst;
using Goo;

namespace Plugster
{

class ElementAdapter : AbstractElementAdapter
{
    private double drag_x;
    private double drag_y;

    CanvasRect background_rect;
    CanvasPath selection_indicator;
    CanvasText title;

    public ElementAdapter(Element elt, CanvasItem parent)
    {
        base(elt);
        drag_x = 0.0;
        drag_y = 0.0;

        Gtk.Style style = parent.get_canvas().get_style();
        CanvasBounds bounds = CanvasBounds();
        canvas_item = CanvasGroup.create(parent);
        canvas_item.button_press_event += on_start_drag;

        ElementData element_data = get_element_data();
        element_data.selected_state_changed += update_selection_indicator;

        double element_x = element_data.x;
        double element_y = element_data.y;
        double element_width = 0.0;
        double element_height = 0.0;

        /////////////////////////////////////////
        // Element title
        Pango.FontDescription font_desc = parent.get_canvas().get_pango_context().get_font_description().copy();
        font_desc.set_weight(Pango.Weight.BOLD);
        title = CanvasText.create(canvas_item, element_data.element.get_name(),
            element_data.x, element_data.y,
            -1,
            Gtk.AnchorType.NORTH_WEST,
            "fill-color", style.fg[Gtk.StateType.NORMAL].to_string(),
            "font-desc", font_desc);
        title.get_bounds(bounds);
        double title_width = bounds.x2 - bounds.x1;
        double title_height = bounds.y2 - bounds.y1;
        element_x -= title_width / 2.0 + DOUBLE_PADDING;
        element_y -= title_height / 2.0 + DOUBLE_PADDING;
        /////////////////////////////////////////

        /////////////////////////////////////////
        // Pads
        double pads_max_width = 0.0;
        double pads_max_height = 0.0;
        int has_sink_pads = 0;
        int has_src_pads = 0;
        var pad_adapters = new GLib.List<PadAdapter>();
        foreach (Pad pad in element_data.element.pads) {
            var pad_adapter = new PadAdapter(pad);
            pad_adapters.append(pad_adapter);
            pads_max_width = double.max(pads_max_width, pad_adapter.get_width());
            pads_max_height = double.max(pads_max_height, pad_adapter.get_height());
            switch(pad.get_direction())
            {
                case PadDirection.UNKNOWN:
                case PadDirection.SINK:
                    has_sink_pads = 1;
                    break;
                case PadDirection.SRC:
                    has_src_pads = 1;
                    break;
            }
        }

        element_width = double.max(title_width, pads_max_width * (has_sink_pads + has_src_pads) + 2.0 * DOUBLE_PADDING)
                        + 2.0 * DOUBLE_PADDING;
        title.x = element_x + (element_width - title_width) / 2.0;
        title.y = element_y + BASE_PADDING;

        double sink_pad_y = element_y + title_height + BASE_PADDING + DOUBLE_PADDING;
        double src_pad_y = sink_pad_y;
        foreach (PadAdapter pad_adapter in pad_adapters) {
            switch(pad_adapter.get_pad().get_direction())
            {
                case PadDirection.UNKNOWN:
                case PadDirection.SINK:
                    pad_adapter.init(element_x, sink_pad_y, pads_max_width, pads_max_height);
                    sink_pad_y += pads_max_height + BASE_PADDING;
                    break;
                case PadDirection.SRC:
                    pad_adapter.init(element_x + element_width - pads_max_width, src_pad_y, pads_max_width, pads_max_height);
                    src_pad_y += pads_max_height + BASE_PADDING;
                    break;
            }
        }
        element_height = double.max(sink_pad_y, src_pad_y) - element_y + DOUBLE_PADDING;
        /////////////////////////////////////////

        /////////////////////////////////////////
        // Element background and bounding box.
        selection_indicator = CanvasPath.create(canvas_item,
            "m %d %d a %d %d 0 0 1 %d -%d h %d a %d %d 0 0 1 %d %d v %d h -%d v -%d".printf((int) element_x, (int) (element_y + DOUBLE_PADDING), (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) (element_width - 2.0 * DOUBLE_PADDING), (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) DOUBLE_PADDING, (int) title_height, (int) element_width, (int) title_height),
            "fill-color", style.bg[Gtk.StateType.SELECTED].to_string(),
            "line-width", 0.0);

        background_rect = CanvasRect.create(canvas_item,
            element_x,
            element_y,
            element_width,
            element_height,
            "fill-color", style.bg[Gtk.StateType.NORMAL].to_string(),
            "line-width", 0.0,
            "radius_x", DOUBLE_PADDING,
            "radius_y", DOUBLE_PADDING);
        background_rect.lower(title);

        CanvasRect.create(canvas_item,
            element_x,
            element_y,
            element_width,
            element_height,
            "stroke-color", style.dark[Gtk.StateType.NORMAL].to_string(),
            "line-width", 2.0,
            "radius_x", DOUBLE_PADDING,
            "radius_y", DOUBLE_PADDING);
        /////////////////////////////////////////

        update_selection_indicator();
    }

    ~ElementAdapter()
    {
        canvas_item.remove();
    }

    private bool on_start_drag(CanvasItem target, Gdk.EventButton event)
    {
        if (event.button == 1) // Left button
        {
            Selection selection = get_element_data().get_selection();
            if ((event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.BUTTON1_MASK)) != 0) {
                selection.toggle(get_element_data().element);
            } else {
                selection.select(get_element_data().element);
            }
            canvas_item.button_release_event += on_end_drag;
            canvas_item.motion_notify_event += on_drag_move;
            drag_x = event.x_root;
            drag_y = event.y_root;
        }
        return false;
    }

    private bool on_end_drag(CanvasItem target, Gdk.EventButton event)
    {
        canvas_item.button_release_event -= on_end_drag;
        canvas_item.motion_notify_event -= on_drag_move;
        drag_x = 0.0;
        drag_y = 0.0;
        return false;
    }

    private bool on_drag_move(CanvasItem target, Gdk.EventMotion event)
    {
        double scale = canvas_item.get_canvas().get_scale();
        double dx = (event.x_root - drag_x) * scale;
        double dy = (event.y_root - drag_y) * scale;
        canvas_item.translate(dx, dy);
        drag_x = event.x_root;
        drag_y = event.y_root;
        return false;
    }

    private void update_selection_indicator()
    {
        ElementData element_data = get_element_data();
        Gtk.Style style = canvas_item.get_canvas().get_style();

        if (element_data.get_selection().contains(element_data.element)) {
            title.fill_color = style.fg[Gtk.StateType.SELECTED].to_string();
            background_rect.stroke_color = style.dark[Gtk.StateType.SELECTED].to_string();
            selection_indicator.raise(background_rect);
            selection_indicator.lower(title);
        } else {
            title.fill_color = style.fg[Gtk.StateType.NORMAL].to_string();
            background_rect.stroke_color = style.dark[Gtk.StateType.NORMAL].to_string();
            selection_indicator.lower(background_rect);
        }
    }
}

}
