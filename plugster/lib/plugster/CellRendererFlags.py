import gobject
import gtk

class CellRendererFlags(gtk.CellRendererText):

    __gproperties__ = {
        'property-param-spec' : (gobject.TYPE_PYOBJECT, "Flags property ParamSpec", "The ParamSpec of the flags property to edit", gobject.PARAM_READWRITE),
        'property-value'      : (gobject.TYPE_PYOBJECT, "Flags property value", "The current value of the flags property to edit", gobject.PARAM_READWRITE),
    }

    def __init__(self):
        gtk.CellRendererText.__init__(self)
        self._property_param_spec = None
        self._property_value = None


    def do_get_property(self, property):
        if property.name == 'property-param-spec':
            return self._property_param_spec
        elif property.name == 'property-value':
            return self._property_value
        else:
            raise AttributeError("unknown property {0}".format(property.name))


    def do_set_property(self, property, value):
        if property.name == 'property-param-spec':
            self._property_param_spec = value
        elif property.name == 'property-value':
            self._property_value = value
            self.props.text = " | ".join(self._property_value.value_names)
        else:
            raise AttributeError("unknown property {0}".format(property.name))


    def start_editing(self, event, widget, path, background_area, cell_area, flags):
        menu = gtk.Menu()
        val = int(self._property_value)
        flags_class = type(self._property_value)
        for mask, flag in flags_class.__flags_values__.iteritems():
            item = gtk.CheckMenuItem(label = flag.first_value_name)
            item.set_active(val & mask == mask)
            item.mask = mask
            item.path = path
            item.connect('toggled', self._on_item_toggled)
            menu.append(item)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)


    def _on_item_toggled(self, menu_item):
        val = 0
        for item in menu_item.props.parent:
            if item.get_active():
                val = val | item.mask
        self.emit('edited', menu_item.path, str(val))

