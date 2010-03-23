import gobject
import gtk
import gst

class ElementFactoriesModel(gtk.TreeStore):

    NAME            = 0
    ELEMENT_FACTORY = 1
    ICON            = 2
    NB_COLUMNS      = 3

    def __init__(self):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gst.ElementFactory, gobject.TYPE_STRING)
        self.set_sort_func(ElementFactoriesModel.NAME, self._compare_items, None)
        self.set_sort_column_id(ElementFactoriesModel.NAME, gtk.SORT_ASCENDING)
        registry = gst.registry_get_default()
        for factory in registry.get_feature_list(gst.ElementFactory):
            parent = self._get_parent_iter(factory.get_klass().split("/"))
            self.append(parent, (factory.get_longname(), factory, gtk.STOCK_CONNECT))


    def _get_parent_iter(self, sections):
        parent = None
        for section in sections:
            section = section.strip()
            current = self.iter_children(parent)
            while current:
                text = self.get(current, ElementFactoriesModel.NAME)[0]
                if section == text:
                    break
                else:
                    current = self.iter_next(current)

            if not current:
                current = self.append(parent, (section, None, gtk.STOCK_DIRECTORY))

            parent = current

        return parent


    def _compare_items(self, tree_model, iter1, iter2, user_data):
        (name1, factory1) = self.get(iter1, ElementFactoriesModel.NAME, ElementFactoriesModel.ELEMENT_FACTORY)
        (name2, factory2) = self.get(iter2, ElementFactoriesModel.NAME, ElementFactoriesModel.ELEMENT_FACTORY)

        if factory1:
            if factory2:
                return cmp(name1.lower(), name2.lower())
            else:
                return 1
        else:
            if factory2:
                return -1
            else:
                return cmp(name1.lower(), name2.lower())
