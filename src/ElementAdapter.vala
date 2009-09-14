using Gst;
using Goo;

namespace Plugster
{

class ElementAdapter : AbstractAdapter
{
    public ElementAdapter(Element elt, CanvasItem parent)
    {
        base(elt);
        CanvasBounds bounds = CanvasBounds();
        canvas_item = CanvasGroup.create(parent);

        double element_x = element_data.x;
        double element_y = element_data.y;
        double element_width = 0.0;
        double element_height = 0.0;

        /////////////////////////////////////////
        // Element title
        var title = CanvasText.create(canvas_item, element_data.element.get_name(), element_data.x, element_data.y, -1, Gtk.AnchorType.NORTH_WEST);
        title.font_desc = title.get_canvas().get_pango_context().get_font_description();
        title.get_bounds(bounds);
        double title_width = bounds.x2 - bounds.x1;
        double title_height = bounds.y2 - bounds.y1;
        element_x -= title_width / 2.0 + double_margin;
        element_y -= title_height / 2.0 + double_margin;
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
            pads_max_width = double.max(pads_max_width, pad_adapter.get_text_width());
            pads_max_height = double.max(pads_max_height, pad_adapter.get_text_height());
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

        element_width = double.max(title_width,
                                   PadAdapter.get_width(pads_max_width) *
                                   (has_sink_pads + has_src_pads) +
                                   quad_margin) + 2.0 * double_margin;
        title.x = element_x + (element_width - title_width) / 2.0;
        title.y = element_y + double_margin;

        double sink_pad_y = element_y + title_height + 2.0 * double_margin;
        double src_pad_y = sink_pad_y;
        foreach (PadAdapter pad_adapter in pad_adapters) {
            switch(pad_adapter.pad.get_direction())
            {
                case PadDirection.UNKNOWN:
                case PadDirection.SINK:
                    pad_adapter.init(element_x, sink_pad_y, pads_max_width, pads_max_height);
                    sink_pad_y += pads_max_height + base_margin;
                    break;
                case PadDirection.SRC:
                    pad_adapter.init(element_x + element_width - pads_max_width, src_pad_y, pads_max_width, pads_max_height);
                    src_pad_y += pads_max_height + base_margin;
                    break;
            }
        }
        element_height = double.max(sink_pad_y, src_pad_y) - element_y + double_margin;
        /////////////////////////////////////////

        /////////////////////////////////////////
        // Element background and bounding box.
        var boundingRect = CanvasRect.create(canvas_item,
            element_x,
            element_y,
            element_width,
            element_height,
            "fill-color", "#ebe2d6", // TODO: get this from the theme
            "radius_x", double_margin,
            "radius_y", double_margin);
        boundingRect.lower(title);
        /////////////////////////////////////////
    }

    ~ElementAdapter()
    {
        canvas_item.remove();
    }
}

}
