import gtk

from ElementFactoriesModel import *

class ElementFactoriesWidget(gtk.TreeView):

    DRAG_TARGETS = [ ('application/x-plugster-element-factory', 0, 0) ]

    def __init__(self):
        gtk.TreeView.__init__(self)

        self.props.width_request = 230

        column = gtk.TreeViewColumn("Element")

        icon_renderer = gtk.CellRendererPixbuf()
        icon_renderer.props.icon_name = 'gtk-open'
        column.pack_start(icon_renderer, False)
        column.add_attribute(icon_renderer, 'icon-name', ElementFactoriesModel.ICON_COLUMN)

        renderer = gtk.CellRendererText()
        column.pack_start(renderer)
        column.add_attribute(renderer, 'text', ElementFactoriesModel.NAME_COLUMN);

        self.append_column(column)

        self.set_tooltip_column(ElementFactoriesModel.TOOLTIP_COLUMN)

        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, ElementFactoriesWidget.DRAG_TARGETS, gtk.gdk.ACTION_COPY)
        self.set_model(ElementFactoriesModel())

        self.connect('drag-data-get', self._drag_data_get_element_factory)


    def _drag_data_get_element_factory(self, widget, drag_context, selection_data, info, timestamp):
        (model, iter) = self.get_selection().get_selected()
        if iter != None and not model.iter_has_child(iter):
            factory = model.get(iter, ElementFactoriesModel.ELEMENT_FACTORY_COLUMN)[0]
            atom = gtk.gdk.atom_intern("application/x-plugster-element-factory", True)
            selection_data.set(atom, 8, factory.get_name())

