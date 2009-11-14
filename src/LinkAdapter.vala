namespace Plugster
{

class LinkAdapter : GLib.Object
{
    private PadAdapter parent_adapter;

    public LinkAdapter(PadAdapter pad_adapter)
    {
        parent_adapter = pad_adapter;
    }
}

}

