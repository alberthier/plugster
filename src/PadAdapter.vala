using Gst;
using Goo;

namespace Plugster
{

class PadAdapter : GLib.Object
{
    public weak Pad pad { get; construct; }
    protected weak CanvasItem canvas_item { get; set; }
    private weak CanvasText text;
    private static const double connector_radius = 5.0;

    public PadAdapter(Pad pad)
    {
        // Initialize ownership and object cleanup.
        this.pad = pad;
        this.pad.weak_ref(unref, this);
        ref();

        ElementAdapter parent = get_parent();
        Canvas canvas = parent.canvas_item.get_canvas();
        canvas_item = CanvasGroup.create(parent.canvas_item);
        text = CanvasText.create(canvas_item, pad.get_name(),
            0, 0,
            -1,
            Gtk.AnchorType.NORTH_WEST,
            "fill-color", canvas.get_style().fg[Gtk.StateType.NORMAL].to_string(),
            "font-desc", canvas.get_pango_context().get_font_description());
    }

    public double get_width()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return bounds.x2 - bounds.x1 + connector_radius + 4.0 * AbstractAdapter.base_margin;
    }

    public double get_height()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return double.max(bounds.y2 - bounds.y1, connector_radius) + 2.0 * AbstractAdapter.base_margin;
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
                text.translate(3.0 * AbstractAdapter.base_margin + connector_radius,
                    height - get_height() + AbstractAdapter.base_margin);
                fill_color = "#73d216";
                connector_x = AbstractAdapter.base_margin + connector_radius / 2.0;
                break;
            case PadDirection.SRC:
                text.translate(width - get_width() + 1.0 * AbstractAdapter.base_margin,
                    height - get_height() + AbstractAdapter.base_margin);
                fill_color = "#f57900";
                connector_x = width - AbstractAdapter.base_margin - connector_radius / 2.0;
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

        if (pad.is_linked()) {
            fill_color = "#204a87";
        } else {
            fill_color = style.bg[Gtk.StateType.NORMAL].to_string();
        }

        CanvasEllipse.create(canvas_item,
            connector_x,
            height / 2.0,
            connector_radius, connector_radius,
            "fill-color", fill_color,
            "stroke-color", style.dark[Gtk.StateType.NORMAL].to_string(),
            "line-width", 2.0);

        canvas_item.translate(x, y);
    }

    private ElementAdapter get_parent()
    {
        return (ElementAdapter) ElementData.get_element_data(pad.get_parent_element()).adapter;
    }
}

}

