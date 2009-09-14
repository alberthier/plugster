using Gst;
using Goo;

namespace Plugster
{

class AbstractAdapter : GLib.Object
{
    protected static const double base_margin = 5.0; // TODO: get this from the theme
    protected static const double double_margin = 2.0 * base_margin;
    protected static const double quad_margin = 2.0 * double_margin;
    protected weak ElementData element_data;
    protected weak CanvasItem canvas_item { get; set; }

    public AbstractAdapter(Element elt)
    {
        var data = ElementData.get_element_data(elt);
        element_data = data;
        element_data.adapter = this;
    }
}

}

