using Gst;
using Goo;

namespace Plugster
{

class PipelineAdapter : AbstractAdapter
{
    private enum Layers {
        ELEMENTS,
        LINKS
    }
    private int element_number;

    public PipelineAdapter(Element elt, Canvas canvas)
    {
        base(elt);
        ((Pipeline) elt).element_added += on_element_added;
        canvas_item = CanvasGroup.create(canvas.get_root_item());
        CanvasGroup.create(canvas_item); // Elements layer
        CanvasGroup.create(canvas_item); // Links layer

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

    private void on_element_added(Element element)
    {
        new ElementAdapter(element, (CanvasItem) ((CanvasGroup) canvas_item).items.index(Layers.ELEMENTS));
    }
}

}

