using Goo;

namespace Plugster
{

class AbstractAdapter : GLib.Object
{
    protected weak CanvasItem canvas_item { get; set; }
    protected weak Gst.Object gst_object { get; set; }
    public static const double BASE_PADDING = 5.0; // TODO: get this from the theme
    public static const double DOUBLE_PADDING = BASE_PADDING * 2.0; // TODO: get this from the theme
    private static const Quark QUARK = Quark.from_string("plugster:adapter");

    public AbstractAdapter(Gst.Object object)
    {
        base(gst_object: object);
        gst_object.set_qdata_full(QUARK, this.ref(), unref);
    }

    public static AbstractAdapter get_adapter(Gst.Object object)
    {
        return (AbstractAdapter) object.get_qdata(QUARK);
    }
}

}

