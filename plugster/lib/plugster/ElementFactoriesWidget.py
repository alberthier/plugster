import gtk

from ElementFactoriesModel import *

class ElementFactoriesWidget(gtk.VBox):

    DRAG_TARGETS = [ ('application/x-plugster-element-factory', 0, 0) ]

    def __init__(self):
        gtk.VBox.__init__(self)

        self._filtered_paths = None
        self._saved_expanded_paths = []

        self._entry = gtk.Entry()
        self._entry.connect("notify::text", self._on_filter_changed)
        self._entry.props.has_frame = False
        self._entry.props.primary_icon_stock = gtk.STOCK_FIND
        self.pack_start(self._entry, False)

        self.pack_start(gtk.HSeparator(), False)

        scroll = gtk.ScrolledWindow()
        scroll.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
        scroll.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
        self.pack_end(scroll)
        self._treeview = gtk.TreeView()
        self._treeview.props.headers_visible = False
        scroll.add(self._treeview)

        self._treeview.props.width_request = 230

        column = gtk.TreeViewColumn("Element")

        icon_renderer = gtk.CellRendererPixbuf()
        icon_renderer.props.icon_name = 'gtk-open'
        column.pack_start(icon_renderer, False)
        column.add_attribute(icon_renderer, 'icon-name', ElementFactoriesModel.ICON_COLUMN)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer)
        column.add_attribute(renderer, 'text', ElementFactoriesModel.NAME_COLUMN);

        self._treeview.append_column(column)

        self._treeview.set_tooltip_column(ElementFactoriesModel.TOOLTIP_COLUMN)

        self._treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, ElementFactoriesWidget.DRAG_TARGETS, gtk.gdk.ACTION_COPY)
        self._model = gtk.TreeModelFilter(child_model = ElementFactoriesModel())
        self._model.set_visible_func(self._is_visible)
        self._treeview.set_model(self._model)

        self._treeview.connect('drag-data-get', self._drag_data_get_element_factory)


    def _drag_data_get_element_factory(self, widget, drag_context, selection_data, info, timestamp):
        (model, iter) = self._treeview.get_selection().get_selected()
        if iter != None and not model.iter_has_child(iter):
            factory = model.get(iter, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)[0]
            atom = gtk.gdk.atom_intern("application/x-plugster-element-factory", True)
            selection_data.set(atom, 8, factory.get_name())


    def _on_filter_changed(self, object, pspec):
        filter = self._entry.props.text
        if len(filter) != 0:
            if self._filtered_paths == None:
                self._treeview.map_expanded_rows(lambda treeview, path: self._saved_expanded_paths.append(path))
            self._filtered_paths = self._filter_children(None, filter.lower())
        else:
            self._filtered_paths = None
        self._model.refilter()
        if len(filter) == 0:
            self._treeview.collapse_all()
            for path in self._saved_expanded_paths:
                self._treeview.expand_row(path, False)
            self._saved_expanded_paths = []
        else:
            self._treeview.expand_all()


    def _filter_children(self, current, filter):
        filtered_paths = []
        model = self._model.props.child_model
        iter = model.iter_children(current)
        if iter != None:
            while iter != None:
                filtered_paths += self._filter_children(iter, filter)
                iter = model.iter_next(iter)
            if len(filtered_paths) != 0:
                if current != None:
                    filtered_paths.append(model.get_path(current))
        else:
            (factory,) = model.get(current, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)
            if filter in factory.get_longname().lower() or \
               filter in factory.get_name().lower():
                filtered_paths.append(model.get_path(current))
        return filtered_paths


    def _is_visible(self, model, iter):
        if self._filtered_paths != None:
            return model.get_path(iter) in self._filtered_paths
        else:
            return True
