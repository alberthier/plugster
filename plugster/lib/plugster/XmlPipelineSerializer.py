import xml.dom

import gobject

from Definitions import *

class XmlPipelineSerializer(object):

    def __init__(self, pipeline):
        object.__init__(self)
        self._pipeline = pipeline
        self._doc = None


    def save(self, filepath):
        self._doc = xml.dom.getDOMImplementation().createDocument(None, "gstreamer", None)
        self._doc.documentElement.setAttribute("xmlns:gst", GST_XML_NAMESPACE)
        self._doc.documentElement.setAttribute("xmlns:plugster", PLUGSTER_XML_NAMESPACE)
        self.create_element_node(self._doc.documentElement, self._pipeline, True)
        self._indent(self._doc.documentElement)
        f = open(filepath, "w")
        f.write(self._doc.toxml(encoding = "UTF-8"))
        f.close()


    def create_element_node(self, parent, gst_element, root):
        doc = parent.ownerDocument
        elt_node = self._create_element(GST_XML_NAMESPACE, "element")

        if not root:
            plugster_data_node = self._create_element(PLUGSTER_XML_NAMESPACE, "data")
            plugster_data_x_node = self._create_element(PLUGSTER_XML_NAMESPACE, "x")
            self._set_element_text(plugster_data_x_node, str(int(gst_element.plugster_data.x)))
            plugster_data_node.appendChild(plugster_data_x_node)
            plugster_data_y_node = self._create_element(PLUGSTER_XML_NAMESPACE, "y")
            self._set_element_text(plugster_data_y_node, str(int(gst_element.plugster_data.y)))
            plugster_data_node.appendChild(plugster_data_y_node)
            elt_node.appendChild(plugster_data_node)

        name_node = self._create_element(GST_XML_NAMESPACE, "name")
        self._set_element_text(name_node, gst_element.get_name())
        elt_node.appendChild(name_node)
        type_node = self._create_element(GST_XML_NAMESPACE, "type")
        self._set_element_text(type_node, gst_element.get_factory().get_name())
        elt_node.appendChild(type_node)

        for pspec in type(gst_element).props:
            if pspec.flags & gobject.PARAM_READWRITE == gobject.PARAM_READWRITE:
                prop_val = gst_element.get_property(pspec.name)
                if pspec.default_value != prop_val:
                    param_node = self._create_element(GST_XML_NAMESPACE, "param")
                    param_name_node = self._create_element(GST_XML_NAMESPACE, "name")
                    self._set_element_text(param_name_node, pspec.name)
                    param_node.appendChild(param_name_node)
                    param_value_node = self._create_element(GST_XML_NAMESPACE, "value")
                    self._set_element_text(param_value_node, self._format_value(pspec, prop_val))
                    param_node.appendChild(param_value_node)
                    elt_node.appendChild(param_node)

        if root:
            children_node = self._create_element(GST_XML_NAMESPACE, "children")
            for elt in gst_element:
                self.create_element_node(children_node, elt, False)
            if len(children_node.childNodes) != 0:
                elt_node.appendChild(children_node)

        parent.appendChild(elt_node)


    def _format_value(self, pspec, value):
        if isinstance(value, gobject.GFlags) or \
           isinstance(value, gobject.GEnum):
            return str(int(value))
        else:
            return str(value)


    def _create_element(self, namespace, tagname):
        if namespace == GST_XML_NAMESPACE:
            prefix = "gst:"
        elif namespace == PLUGSTER_XML_NAMESPACE:
            prefix = "plugster:"
        return self._doc.createElementNS(namespace, prefix + tagname)


    def _set_element_text(self, dom_element, text):
        return dom_element.appendChild(self._doc.createTextNode(text))


    def _indent(self, element, indent = "\n"):
        if element.nodeType == xml.dom.Node.ELEMENT_NODE and \
           (element.tagName == "gstreamer" or \
            element.tagName == "gst:element" or \
            element.tagName == "gst:children" or \
            element.tagName == "gst:param" or \
            element.tagName == "plugster:data"):
            child_indent = indent + "  "
            index = 0
            while index < len(element.childNodes):
                child = element.childNodes[index]
                text = self._doc.createTextNode(child_indent)
                element.insertBefore(text, child)
                index += 2
                self._indent(child, child_indent)
                if index == len(element.childNodes):
                    text = self._doc.createTextNode(indent)
                    element.appendChild(text)
                    index += 1

