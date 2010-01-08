using Gtk;
using Goo;

namespace Plugster
{

class PipelineCanvas : Canvas
{
    public static const int GRID_SIZE = 20;

    construct
    {
        Gtk.drag_dest_set(this, Gtk.DestDefaults.ALL, ElementFactoriesWidget.drag_targets, Gdk.DragAction.COPY);
        automatic_bounds = true;
        integer_layout = true;
    }

    public static void place_on_grid(CanvasItem item, double move_x, double move_y)
    {
        stdout.printf("(%f, %f) -> (%f, %f)\n", move_x, move_y, place_coord_on_grid(move_x), place_coord_on_grid(move_y)    );
        item.translate(place_coord_on_grid(move_x), place_coord_on_grid(move_y));
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
