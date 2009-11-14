using Gst;
using Goo;

namespace Plugster
{

class PadAdapter : GLib.Object
{
    public weak Pad pad { get; construct; }
    public weak LinkAdapter? link_adapter {get; set; }
    protected weak CanvasItem canvas_item { get; set; }
    private weak CanvasText text;
    private weak CanvasEllipse connector;
    private static const double CONNECTOR_RADIUS = 5.0;
    private static const Quark QUARK = Quark.from_string("plugster:pad-adapter");

    public PadAdapter(Pad gst_pad)
    {
        GLib.Object(pad: gst_pad);
        // Initialize ownership and object cleanup.
        pad.set_qdata_full(QUARK, this.ref(), unref);

        ElementAdapter parent = get_parent();
        Canvas canvas = parent.canvas_item.get_canvas();
        canvas_item = CanvasGroup.create(parent.canvas_item);
        canvas_item.button_press_event += on_start_drag;

        text = CanvasText.create(canvas_item, pad.get_name(),
            0, 0,
            -1,
            Gtk.AnchorType.NORTH_WEST,
            "fill-color", canvas.get_style().fg[Gtk.StateType.NORMAL].to_string(),
            "font-desc", canvas.get_pango_context().get_font_description());

        pad.linked += on_pad_linked;
        pad.unlinked += on_pad_unlinked;
    }

    public double get_width()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return bounds.x2 - bounds.x1 + CONNECTOR_RADIUS + 4.0 * AbstractAdapter.base_margin;
    }

    public double get_height()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return double.max(bounds.y2 - bounds.y1, CONNECTOR_RADIUS) + 2.0 * AbstractAdapter.base_margin;
    }

    public void init(double x, double y, double width, double height)
    {
        Gtk.Style style = canvas_item.get_canvas().get_style();
        string fill_color = "";
        double connector_x = 0.0;
        switch(pad.get_direction())
        {
            case PadDirection.UNKNOWN:
            case PadDirection.SINK:
                text.translate(3.0 * AbstractAdapter.base_margin + CONNECTOR_RADIUS,
                    height - get_height() + AbstractAdapter.base_margin);
                fill_color = "#73d216";
                connector_x = AbstractAdapter.base_margin + CONNECTOR_RADIUS / 2.0;
                break;
            case PadDirection.SRC:
                text.translate(width - get_width() + 1.0 * AbstractAdapter.base_margin,
                    height - get_height() + AbstractAdapter.base_margin);
                fill_color = "#f57900";
                connector_x = width - AbstractAdapter.base_margin - CONNECTOR_RADIUS / 2.0;
                break;
        }
        var boundingRect = CanvasRect.create(canvas_item,
            0, 0,
            width, height,
            "fill-color", fill_color,
            "line-width", 0.0,
            "radius_x", AbstractAdapter.base_margin,
            "radius_y", AbstractAdapter.base_margin);
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

    private ElementAdapter get_parent()
    {
        return (ElementAdapter) ElementData.get_element_data(pad.get_parent_element()).adapter;
    }

    public static PadAdapter get_pad_adapter(Pad pad)
    {
        return (PadAdapter) pad.get_qdata(QUARK);
    }

    private string get_connector_color()
    {
        if (pad.is_linked()) {
            return "#204a87";
        } else {
            Gtk.Style style = canvas_item.get_canvas().get_style();
            return style.bg[Gtk.StateType.NORMAL].to_string();
        }
    }

    private void on_pad_linked(Pad peer)
    {
        connector.fill_color = get_connector_color();
        if (pad.get_direction() == PadDirection.SRC) {
            link_adapter = (LinkAdapter) new LinkAdapter().ref();
            link_adapter.src_pad_adapter = this;
            link_adapter.dst_pad_adapter = get_pad_adapter(peer);
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
        if (pad.get_direction() == PadDirection.SRC) {
            link_adapter.src_pad_adapter = this;
        } else {
            link_adapter.dst_pad_adapter = this;
        }
        link_adapter.unref();
        return true;
    }
}

}

