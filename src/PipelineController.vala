using Gst;
using Gtk;
using Goo;

namespace Plugster
{

class PipelineController : GLib.Object
{
    private Window  root_widget;
    private PipelineCanvas canvas;
    public  Pipeline root_pipeline;
    private string  filepath;
    private static const string root_pipeline_name = "plugster_root";

    public PipelineController(Window root_win, PipelineCanvas canvas)
    {
        this.root_widget = root_win;
        this.canvas = canvas;
    }

    public void reset()
    {
        filepath = null;
        configure_new_root_pipeline(new Pipeline(root_pipeline_name + "_new"));
    }

    public void open()
    {
        reset();
        filepath = get_filepath("Open", FileChooserAction.OPEN);
        if (filepath != null) {
            var xml = new XML();
            xml.object_loaded += ElementData.load;
            if (xml.parse_file(filepath, root_pipeline_name)) {
                unowned GLib.List<unowned Element> elements = xml.get_topelements();
                if (elements.length() > 0) {
                    Element first = elements.first().data;
                    configure_new_root_pipeline(first);
                    // TODO: Why do I have to unref the element manually?
                    first.unref();
                    first.unref();
                }
            }
        }
    }

    public void save()
    {
        if (filepath == null) {
            save_as();
        } else {
            var xml = new XML();
            var file = FileStream.open(filepath, "w");
            if (file != null) {
                xml.write_file(root_pipeline, file);
            } else {
                var dialog = new MessageDialog(root_widget, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, "Unable to open the file '%s'", filepath);
                dialog.run();
                dialog.close();
                filepath = null;
            }
        }
    }

    public void save_as()
    {
        string path = get_filepath("Save", FileChooserAction.SAVE);
        if (path != null) {
            filepath = path;
            save();
        }
    }

    private string? get_filepath(string text, FileChooserAction action)
    {
        string icon;
        if (action == FileChooserAction.SAVE) {
            icon = STOCK_SAVE;
        } else {
            icon = STOCK_OPEN;
        }
        var dialog = new FileChooserDialog(text, root_widget, action, STOCK_CANCEL, ResponseType.CANCEL, icon, ResponseType.ACCEPT);
        dialog.set_select_multiple(false);
        FileFilter filter = new FileFilter();
        filter.add_mime_type("application/xml");
        dialog.set_filter(filter);
        string? filename = null;
        if (dialog.run() == ResponseType.ACCEPT) {
            filename = dialog.get_filename();
        }
        dialog.close();
        return filename;
    }

    private void configure_new_root_pipeline(Element elt)
    {
        if (elt is Pipeline) {
            root_pipeline = (Pipeline) elt;
            new ElementData(root_pipeline);
            root_pipeline.element_added += on_element_added;
            new PipelineAdapter(root_pipeline, canvas);
        }
    }

    private void on_element_added(Element element)
    {
        new ElementAdapter(element, canvas.get_root_item());
    }
}

}

