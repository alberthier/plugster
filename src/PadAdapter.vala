using Gst;
using Goo;

namespace Plugster
{

class PadAdapter : AbstractAdapter
{
    private weak CanvasText text;
    private weak CanvasEllipse connector;
    private weak CanvasPolyline? link;
    private static const double CONNECTOR_RADIUS = 5.0;

    public PadAdapter(Pad gst_pad)
    {
        base(gst_pad);

        AbstractElementAdapter parent = get_parent_adapter();
        Canvas canvas = parent.canvas_item.get_canvas();
        canvas_item = CanvasGroup.create(parent.canvas_item);
        canvas_item.button_press_event += on_start_drag;

        text = CanvasText.create(canvas_item, gst_pad.get_name(),
            0, 0,
            -1,
            Gtk.AnchorType.NORTH_WEST,
            "fill-color", canvas.get_style().fg[Gtk.StateType.NORMAL].to_string(),
            "font-desc", canvas.get_pango_context().get_font_description());

        gst_pad.linked += on_pad_linked;
        gst_pad.unlinked += on_pad_unlinked;
    }

    public Pad get_pad()
    {
        return (Pad) gst_object;
    }

    public static PadAdapter get_pad_adapter(Pad pad)
    {
        return (PadAdapter) AbstractAdapter.get_adapter(pad);
    }

    public static PadAdapter? get_pad_adapter_from_item(CanvasItem item)
    {
        return (PadAdapter) AbstractAdapter.get_adapter_from_item(item);
    }

    public PadAdapter? get_pad_adapter_at(double x, double y)
    {
        PadAdapter? found;
        weak GLib.List<CanvasItem> items = canvas_item.get_canvas().get_items_at(x, y, false);
        foreach (CanvasItem item in items) {
            found = get_pad_adapter_from_item(item);
            if (found != null) {
                return found;
            }
        }
        return null;
    }

    public double get_width()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(out bounds);
        return bounds.x2 - bounds.x1 + CONNECTOR_RADIUS + 4.0 * BASE_PADDING;
    }

    public double get_height()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(out bounds);
        return double.max(bounds.y2 - bounds.y1, CONNECTOR_RADIUS) + 2.0 * BASE_PADDING;
    }

    public void init(double x, double y, double width, double height)
    {
        Gtk.Style style = canvas_item.get_canvas().get_style();
        string fill_color = "";
        double connector_x = 0.0;
        switch(get_pad().get_direction())
        {
            case PadDirection.UNKNOWN:
            case PadDirection.SINK:
                text.translate(3.0 * BASE_PADDING + CONNECTOR_RADIUS,
                    height - get_height() + BASE_PADDING);
                fill_color = "#73d216";
                connector_x = BASE_PADDING + CONNECTOR_RADIUS / 2.0;
                break;
            case PadDirection.SRC:
                text.translate(width - get_width() + 1.0 * BASE_PADDING,
                    height - get_height() + BASE_PADDING);
                fill_color = "#f57900";
                connector_x = width - BASE_PADDING - CONNECTOR_RADIUS / 2.0;
                break;
        }
        var boundingRect = CanvasRect.create(canvas_item,
            0, 0,
            width, height,
            "fill-color", fill_color,
            "line-width", 0.0,
            "radius_x", BASE_PADDING,
            "radius_y", BASE_PADDING);
        boundingRect.lower(text);

        connector = CanvasEllipse.create(canvas_item,
            connector_x,
            height / 2.0,
            CONNECTOR_RADIUS, CONNECTOR_RADIUS,
            "fill-color", get_connector_color(),
            "stroke-color", style.dark[Gtk.StateType.NORMAL].to_string(),
            "line-width", 2.0);

        canvas_item.translate(x, y);
    }

    private AbstractElementAdapter get_parent_adapter()
    {
        return (AbstractElementAdapter) AbstractAdapter.get_adapter(get_pad().get_parent_element());
    }

    private string get_connector_color()
    {
        if (get_pad().is_linked()) {
            return "#204a87";
        } else {
            Gtk.Style style = canvas_item.get_canvas().get_style();
            return style.bg[Gtk.StateType.NORMAL].to_string();
        }
    }

    private void on_pad_linked(Pad peer)
    {
        stdout.printf("on_pad_linked\n");
        connector.fill_color = get_connector_color();
        if (get_pad().get_direction() == PadDirection.SRC) {
            double x;
            double y;
            connector.get("x", out x, "y", out y);
            link = CanvasPolyline.create_line(canvas_item, x, y, x, y);
        }
    }

    private void on_pad_unlinked(Pad peer)
    {
        stdout.printf("on_pad_unlinked\n");
        connector.fill_color = get_connector_color();
        link = null;
    }

    private bool on_start_drag(CanvasItem target, Gdk.EventButton event)
    {
        canvas_item.button_release_event += on_end_drag;
        canvas_item.motion_notify_event += on_drag_move;
        double x;
        double y;
        connector.get("x", out x, "y", out y);
        link = CanvasPolyline.create_line(canvas_item, x, y, x, y);
        PipelineAdapter pipeline_adapter = PipelineAdapter.get_pipeline_adapter(get_parent_adapter().get_element_data().get_pipeline());
        link.raise(null);
        return true;
    }

    public bool on_drag_move(CanvasItem target, Gdk.EventMotion event)
    {
        CanvasPoints points = link.points;
        ((double*) points.coords)[2] = event.x;
        ((double*) points.coords)[3] = event.y;
        link.points = points;
        return false;
    }

    public bool on_end_drag(CanvasItem target, Gdk.EventButton event)
    {
        if (link != null) {
            link.remove();
            link = null;
        }
        Canvas canvas = canvas_item.get_canvas();
        PadAdapter? peer_adapter = get_pad_adapter_at(event.x, event.y);
        if (peer_adapter != null) {
            Pad pad = get_pad();
            if (pad.get_direction() == PadDirection.SRC) {
                pad.link(peer_adapter.get_pad());
            } else {
                peer_adapter.get_pad().link(pad);
            }
        }

        canvas_item.motion_notify_event -= on_drag_move;
        canvas_item.button_release_event -= on_end_drag;
        return false;
    }
}

}

