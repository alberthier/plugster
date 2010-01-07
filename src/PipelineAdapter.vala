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
        element_numbers = new HashTable<string, int>.full(GLib.str_hash, GLib.str_equal, release_hash_items, null);
        canvas_item = CanvasGroup.create(canvas.get_root_item());
        elements_layer = CanvasGroup.create(canvas_item);
        links_layer = CanvasGroup.create(canvas_item);

        pipeline.element_added += on_element_added;
        canvas.drag_data_received += create_new_element;
        canvas.button_press_event += on_button_pressed;
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
            int n = element_numbers.lookup(factory_name) + 1;
            element_numbers.insert(factory_name, n);
            Element elt = ElementFactory.make(factory_name, "%s-%d".printf(factory_name, n));
            ElementData data = new ElementData(elt);
            data.x = x;
            data.y = y;
            get_pipeline().add(elt);
            Selection selection = data.get_selection();
            selection.select(elt);
        }
    }

    private void on_element_added(Element element)
    {
        new ElementAdapter(element, elements_layer);
    }

    private bool on_button_pressed(Gdk.EventButton event)
    {
        if (event.button == 1) // Left button
        {
            if (links_layer.canvas.get_items_at(event.x, event.y, false) == null) {
                Selection.get_selection(get_pipeline()).clear();
            }
        }
        return false;
    }

    private static void release_hash_items(void* data)
    {
        free(data);
    }
}

}

