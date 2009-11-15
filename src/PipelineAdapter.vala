using Gst;
using Goo;

namespace Plugster
{

class PipelineAdapter : AbstractElementAdapter
{
    private weak CanvasGroup elements_layer;
    private weak CanvasGroup links_layer;
    private int element_number;

    public PipelineAdapter(Pipeline pipeline, Canvas canvas)
    {
        base(pipeline);
        pipeline.element_added += on_element_added;
        canvas_item = CanvasGroup.create(canvas.get_root_item());
        elements_layer = CanvasGroup.create(canvas_item);
        links_layer = CanvasGroup.create(canvas_item);

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
            Element elt = ElementFactory.make(factory_name, "%s-%d".printf(factory_name, element_number++));
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

