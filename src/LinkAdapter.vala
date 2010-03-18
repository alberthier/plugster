using Goo;

namespace Plugster
{

class LinkAdapter : GLib.Object
{
    public weak PadAdapter? src_pad_adapter { get; set; }
    public weak PadAdapter? dst_pad_adapter { get; set; }

    public LinkAdapter()
    {
    }

    public bool on_drag_move(CanvasItem target, Gdk.EventMotion event)
    {
        return false;
    }

    public bool on_end_drag(CanvasItem target, Gdk.EventButton event)
    {
        src_pad_adapter.canvas_item.motion_notify_event -= on_drag_move;
        src_pad_adapter.canvas_item.button_release_event -= on_end_drag;
        dst_pad_adapter.canvas_item.motion_notify_event -= on_drag_move;
        dst_pad_adapter.canvas_item.button_release_event -= on_end_drag;
        return false;
    }
}

}

