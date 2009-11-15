using Gst;
using Goo;

namespace Plugster
{

class PipelineAdapter : AbstractElementAdapter
{
    private weak CanvasGroup elements_layer;
    private weak CanvasGroup links_layer;
    private HashTable<string, int> element_numbers;

    public PipelineAdapter(Pipeline pipeline, Canvas canvas)
    {
        base(pipeline);
        element_numbers = new HashTable<string, int>(GLib.str_hash, GLib.str_equal);
        canvas_item = CanvasGroup.create(canvas.get_root_item());
        elements_layer = CanvasGroup.create(canvas_item);
        links_layer = CanvasGroup.create(canvas_item);

        pipeline.element_added += on_element_added;
        canvas.drag_data_received += create_new_element;
    }

    public Pipeline get_pipeline()
    {
        return (Pipeline) gst_object;
    }

    private void create_new_element(Gdk.DragContext context, int x, int y, Gtk.SelectionData selection_data, uint info, uint time)
    {
        if (selection_data.type == Gdk.Atom.intern("application/x-plugster-element-factory", true)) {
            string factory_name = (string) selection_data.data;
            Gtk.drag_finish(context, true, false, time);
            int n = element_numbers.lookup(factory_name);
            element_numbers.insert(factory_name, ++n);
            Element elt = ElementFactory.make(factory_name, "%s-%d".printf(factory_name, n));
            ElementData data = new ElementData(elt);
            data.x = x;
            data.y = y;
            get_pipeline().add(elt);
        }
    }

    private void on_element_added(Element element)
    {
        new ElementAdapter(element, elements_layer);
    }
}

}

