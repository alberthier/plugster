using Gst;
using Goo;

namespace Plugster
{

class PipelineAdapter : AbstractAdapter
{
    private int element_number;

    public PipelineAdapter(Element elt, Canvas canvas)
    {
        base(elt);
        canvas_item = canvas.get_root_item();
        canvas.drag_data_received += create_new_element;
    }

    private void create_new_element(Gdk.DragContext context, int x, int y, Gtk.SelectionData selection_data, uint info, uint time)
    {
        if (selection_data.type == Gdk.Atom.intern("application/x-plugster-element-factory", true)) {
            string factory_name = (string) selection_data.data;
            Gtk.drag_finish(context, true, false, time);
            Element elt = ElementFactory.make(factory_name, "%s-%d".printf(factory_name, element_number++));
            ElementData data = new ElementData(elt);
            data.x = x;
            data.y = y;
            ((Pipeline) element_data.element).add(elt);
        }
    }
}

}

