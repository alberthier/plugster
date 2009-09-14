using Gtk;
using Goo;

namespace Plugster
{

class PipelineCanvas : Canvas
{
    construct
    {
        Gtk.drag_dest_set(this, Gtk.DestDefaults.ALL, ElementFactoriesWidget.drag_targets, Gdk.DragAction.COPY);
        automatic_bounds = true;
        integer_layout = true;
    }
}

}
