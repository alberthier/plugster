import glib
import gobject
import gtk
import gst

class ElementFactoriesModel(gtk.TreeStore):

    NAME_COLUMN            = 0
    ELEMENT_FACTORY_COLUMN = 1
    ICON_COLUMN            = 2
    TOOLTIP_COLUMN         = 3
    NB_COLUMNS             = 4

    def __init__(self):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gst.ElementFactory, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.set_sort_func(ElementFactoriesModel.NAME_COLUMN, self._compare_items, None)
        self.set_sort_column_id(ElementFactoriesModel.NAME_COLUMN, gtk.SORT_ASCENDING)
        registry = gst.registry_get_default()
        for plugin in registry.get_plugin_list():
            for feature in registry.get_feature_list_by_plugin(plugin.get_name()):
                if isinstance(feature, gst.ElementFactory):
                    feature.plugin = plugin
                    parent = self._get_parent_iter(feature.get_klass().split("/"))
                    self.append(parent, (feature.get_longname(), feature, gtk.STOCK_CONNECT, glib.markup_escape_text(feature.get_description())))


    def _get_parent_iter(self, sections):
        parent = None
        for section in sections:
            section = section.strip()
            current = self.iter_children(parent)
            while current != None:
                text = self.get(current, ElementFactoriesModel.NAME_COLUMN)[0]
                if section == text:
                    break
                else:
                    current = self.iter_next(current)

            if current == None:
                current = self.append(parent, (section, None, gtk.STOCK_DIRECTORY, None))

            parent = current

        return parent


    def _compare_items(self, tree_model, iter1, iter2, user_data):
        (name1, factory1) = self.get(iter1, ElementFactoriesModel.NAME_COLUMN, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)
        (name2, factory2) = self.get(iter2, ElementFactoriesModel.NAME_COLUMN, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)

        if factory1 != None:
            if factory2 != None:
                return cmp(name1.lower(), name2.lower())
            else:
                return 1
        else:
            if factory2 != None:
                return -1
            else:
                return cmp(name1.lower(), name2.lower())
