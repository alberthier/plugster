import gtk

from ElementFactoriesModel import *

class ElementFactoriesWidget(gtk.VBox):

    DRAG_TARGETS = [ ('application/x-plugster-element-factory', 0, 0) ]

    def __init__(self):
        gtk.VBox.__init__(self)

        self._entry = gtk.Entry()
        self._entry.connect("notify::text", self._on_filter_changed)
        self.pack_start(self._entry, False)

        scroll = gtk.ScrolledWindow()
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
        self._treeview.set_model(ElementFactoriesModel())

        self._treeview.connect('drag-data-get', self._drag_data_get_element_factory)


    def _drag_data_get_element_factory(self, widget, drag_context, selection_data, info, timestamp):
        (model, iter) = self._treeview.get_selection().get_selected()
        if iter != None and not model.iter_has_child(iter):
            factory = model.get(iter, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)[0]
            atom = gtk.gdk.atom_intern("application/x-plugster-element-factory", True)
            selection_data.set(atom, 8, factory.get_name())


    def _on_filter_changed(self, object, pspec):
        print self._entry.props.text
