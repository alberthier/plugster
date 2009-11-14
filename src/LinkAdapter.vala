namespace Plugster
{

class LinkAdapter : GLib.Object
{
    private weak PadAdapter? m_src_pad_adapter;
    private weak PadAdapter? m_dst_pad_adapter;
    public weak PadAdapter? src_pad_adapter
    {
        get { return m_src_pad_adapter; }
        set
        {
            if (m_dst_pad_adapter == null && m_src_pad_adapter == null && value != null) {
                ref();
            }
            m_src_pad_adapter = value;
            m_src_pad_adapter.weak_ref(on_src_deleted, this);
        }
    }
    public weak PadAdapter? dst_pad_adapter
    {
        get { return m_dst_pad_adapter; }
        set
        {
            if (m_src_pad_adapter == null && m_dst_pad_adapter == null && value != null) {
                ref();
            }
            m_dst_pad_adapter = value;
            m_dst_pad_adapter.weak_ref(on_dst_deleted, this);
        }
    }

    public LinkAdapter()
    {
    }

    private static void on_src_deleted(void* self, Object deleted)
    {
        LinkAdapter* adapter = (LinkAdapter*) (self);
        if (adapter->m_dst_pad_adapter != null) {
           adapter->m_dst_pad_adapter.link_adapter = null;
        }
    }

    private static void on_dst_deleted(void* self, Object deleted)
    {
        LinkAdapter* adapter = (LinkAdapter*) (self);
        if (adapter->m_src_pad_adapter != null) {
           adapter->m_src_pad_adapter.link_adapter = null;
        }
    }
}

}

