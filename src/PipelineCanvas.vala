using Gtk;
using Goo;

namespace Plugster
{

class PipelineCanvas : Canvas
{
    public static const int GRID_SIZE = 20;

    public PipelineCanvas()
    {
        Gtk.drag_dest_set(this, Gtk.DestDefaults.ALL, ElementFactoriesWidget.drag_targets, Gdk.DragAction.COPY);
        automatic_bounds = true;
        integer_layout = true;
    }

    public static double place_coord_on_grid(double coord)
    {
        int quo;
        double delta = Math.remquof((float) coord, (float) PipelineCanvas.GRID_SIZE, out quo);
        if ((float) delta < ((double) PipelineCanvas.GRID_SIZE) / 2.0)
        {
            delta = -delta;
        } else {
            delta = ((double) PipelineCanvas.GRID_SIZE) - delta;
        }
        return delta;
    }
}

}
