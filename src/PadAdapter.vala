using Gst;
using Goo;

namespace Plugster
{

class PadAdapter : GLib.Object
{
    public weak Pad pad { get; construct; }
    protected weak CanvasItem canvas_item { get; set; }
    private weak CanvasText text;

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

    public double get_text_width()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return bounds.x2 - bounds.x1;
    }

    public double get_text_height()
    {
        CanvasBounds bounds = CanvasBounds();
        text.get_bounds(bounds);
        return bounds.y2 - bounds.y1;
    }

    public static double get_width(double text_width)
    {
        return text_width;
    }

    public static double get_height(double text_height)
    {
        return text_height;
    }

    public void init(double x, double y, double width, double height)
    {
        canvas_item.translate(x, y);
    }

    private ElementAdapter get_parent()
    {
        return (ElementAdapter) ElementData.get_element_data(pad.get_parent_element()).adapter;
    }
}

}

