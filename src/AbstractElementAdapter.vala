using Gst;

namespace Plugster
{

class AbstractElementAdapter : AbstractAdapter
{
    public AbstractElementAdapter(Element element)
    {
        base(element);
    }

    public ElementData get_element_data()
    {
        return ElementData.get_element_data((Element) gst_object);
    }

    public Element get_element()
    {
        return (Element) gst_object;
    }

    public static AbstractElementAdapter get_abstract_element_adapter(Element elt)
    {
        return (AbstractElementAdapter) AbstractAdapter.get_adapter(elt);
    }
}

}

