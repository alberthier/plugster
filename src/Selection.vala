using Gst;

namespace Plugster
{
    class Selection : GLib.Object
    {
        public weak Pipeline pipeline { get; set; }
        private GLib.List<weak Element> selected_elements;
        private static const Quark QUARK = Quark.from_string("plugster:selection");

        public signal void selection_changed();

        public Selection(Pipeline pipe)
        {
            pipeline = pipe;
            selected_elements = new GLib.List<weak Element>();
            pipeline.set_qdata_full(QUARK, this.ref(), unref);
            pipeline.element_removed += remove;
        }

        public static Selection get_selection(Pipeline pipe)
        {
            return (Selection) pipe.get_qdata(QUARK);
        }

        public void add(Element elt)
        {
            if (!contains(elt)) {
                selected_elements.append(elt);
                ElementData.get_element_data(elt).selected_state_changed();
                selection_changed();
            }
        }

        public void remove(Element elt)
        {
            if (contains(elt)) {
                selected_elements.remove(elt);
                ElementData.get_element_data(elt).selected_state_changed();
                selection_changed();
            }
        }

        public void clear()
        {
            GLib.List<weak Element> previously_selected_elements = (owned) selected_elements;
            selected_elements = new GLib.List<weak Element>();
            foreach (Element elt in previously_selected_elements) {
                ElementData.get_element_data(elt).selected_state_changed();
            }
            selection_changed();
        }

        public void select(Element elt)
        {
            clear();
            add(elt);
        }

        public void toggle(Element elt)
        {
            if (contains(elt)) {
                remove(elt);
            } else {
                add(elt);
            }
        }

        public bool contains(Element elt)
        {
            return selected_elements.find(elt) != null;
        }

        public unowned GLib.List<weak Element> get_selected_elements()
        {
            return selected_elements;
        }
    }
}

