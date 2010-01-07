using Gst;

namespace Plugster
{

class ElementData : GLib.Object
{
    public weak Element element { get; construct; }
    public int x { get; set; }
    public int y { get; set; }
    private static const Quark QUARK = Quark.from_string("plugster:element-data");
    private static const string XML_NS            = "plugster";
    private static const string XML_COORDS_TAG    = "coords";
    private static const string XML_HREF          = "http://gstreamer.net/plugster/1.0/";
    private static const string XML_COORDS_X_TAG  = "x";
    private static const string XML_COORDS_Y_TAG  = "y";

    public signal void selected_state_changed();

    public ElementData(Element elt)
    {
        GLib.Object(element: elt);
        element.set_qdata_full(QUARK, this.ref(), unref);
        element.object_saved += save_coords;
    }

    public static void load(Gst.Object object, void* self)
    {
        if (object is Element) {
            Element element = (Element) object;
            Xml.Node* xml_node = (Xml.Node*) self;
            if (xml_node->type == Xml.ElementType.ELEMENT_NODE) {
                int x = -1;
                int y = -1;
                Xml.Element* xml_element = (Xml.Element*) xml_node;
                Xml.Node* xml_child = xml_element->children;
                while(xml_child != null) {
                    if (ckeck_xml_node(xml_child) && xml_child->name == XML_COORDS_TAG) {
                        Xml.Node* xml_coords = xml_child->children;
                        while (xml_coords != null) {
                            if (ckeck_xml_node(xml_coords)) {
                                switch(xml_coords->name) {
                                    case XML_COORDS_X_TAG:
                                        x = xml_coords->get_content().to_int();
                                        break;
                                    case XML_COORDS_Y_TAG:
                                        y = xml_coords->get_content().to_int();
                                        break;
                                }
                            }
                            xml_coords = xml_coords->next;
                        }
                        break;
                    }
                    xml_child = xml_child->next;
                }
                ElementData ed = new ElementData(element);
                ed.x = x;
                ed.y = y;
            }
        }
    }

    public Pipeline get_pipeline()
    {
        if (element is Pipeline) {
            return (Pipeline) element;
        } else {
            return get_element_data((Element) element.parent).get_pipeline();
        }
    }

    public Selection get_selection()
    {
        return Selection.get_selection(get_pipeline());
    }

    public static ElementData get_element_data(Element elt)
    {
        return (ElementData) elt.get_qdata(QUARK);
    }

    private static bool ckeck_xml_node(Xml.Node* node)
    {
        return node->type == Xml.ElementType.ELEMENT_NODE
                && node->ns->type == Xml.ElementType.ELEMENT_NODE
                && node->ns->href == XML_HREF
                && node->ns->prefix == XML_NS;
    }

    private void save_coords(Xml.Node* parent)
    {
        Xml.Ns* xml_namespace = Xml.Ns.create(parent->doc->get_root_element(), XML_HREF, XML_NS);

        Xml.Node* coords_node = new Xml.Node(xml_namespace, XML_COORDS_TAG);
        parent->add_child(coords_node);
        Xml.Node* coord = new Xml.Node(xml_namespace, XML_COORDS_X_TAG);
        coord->set_content(x.to_string());
        coords_node->add_child(coord);
        coord = new Xml.Node(xml_namespace, XML_COORDS_Y_TAG);
        coord->set_content(y.to_string());
        coords_node->add_child(coord);
    }
}

}

