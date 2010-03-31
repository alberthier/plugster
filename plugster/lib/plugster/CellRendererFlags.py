import gobject
import gtk

class CellRendererFlags(gtk.CellRendererText):

    __gsignals__ = {
        # edited signal: (path, new_value)
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

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
            text = ""
            for val in self._property_value:
                if val != None:
                    if val != 0:
                        if len(text) != 0:
                            text += " | "
                        text += val.first_value_name
                else:
                    text = "---"
                    break;
            self.props.text = text
        else:
            raise AttributeError("unknown property {0}".format(property.name))


    def start_editing(self, event, widget, path, background_area, cell_area, flags):
        menu = gtk.Menu()
        menu.path = path
        for index, (mask, flag)in enumerate(self._property_param_spec.flags_class.__flags_values__.iteritems()):
            item = gtk.CheckMenuItem(label = flag.first_value_name)
            val = self._property_value[index]
            if val != None:
                item.set_active(val != 0)
            else:
                item.set_inconsistent(True)
            item.flag = flag
            item.index = index
            item.connect('toggled', self._on_item_toggled)
            menu.append(item)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)


    def _on_item_toggled(self, menu_item):
        if menu_item.get_active():
            self._property_value[menu_item.index] = menu_item.flag
        else:
            self._property_value[menu_item.index] = 0
        self.emit('changed', menu_item.props.parent.path, self._property_value)

