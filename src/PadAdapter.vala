using Gst;
using Goo;

namespace Plugster
{

class PadAdapter : AbstractAdapter
{
    public weak LinkAdapter? link_adapter {get; set; }
    private weak CanvasText text;
    private weak CanvasEllipse connector;
    private static const double CONNECTOR_RADIUS = 5.0;

    public PadAdapter(Pad gst_pad)
    {
        base(gst_pad);

        ElementAdapter parent = get_parent_adapter();
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

    public double get_width()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return bounds.x2 - bounds.x1 + CONNECTOR_RADIUS + 4.0 * BASE_PADDING;
    }

    public double get_height()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
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

    private ElementAdapter get_parent_adapter()
    {
        return (ElementAdapter) AbstractAdapter.get_adapter(get_pad().get_parent_element());
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
        connector.fill_color = get_connector_color();
        if (get_pad().get_direction() == PadDirection.SRC) {
            link_adapter = (LinkAdapter) new LinkAdapter().ref();
            link_adapter.src_pad_adapter = this;
            link_adapter.dst_pad_adapter = (PadAdapter) AbstractAdapter.get_adapter(peer);
            link_adapter.unref();
        }
    }

    private void on_pad_unlinked(Pad peer)
    {
        connector.fill_color = get_connector_color();
        link_adapter = null;
    }

    private bool on_start_drag(CanvasItem target, Gdk.EventButton event)
    {
        link_adapter = (LinkAdapter) new LinkAdapter().ref();
        if (get_pad().get_direction() == PadDirection.SRC) {
            link_adapter.src_pad_adapter = this;
        } else {
            link_adapter.dst_pad_adapter = this;
        }
        link_adapter.unref();
        return true;
    }
}

}

