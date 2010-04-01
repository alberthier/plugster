import gobject
import gtk

class CellRendererPropertyName(gtk.CellRendererText):

    __gproperties__ = {
        'active' : (gobject.TYPE_BOOLEAN, "Flag defining if the property is active", "Flag defining if the property is active", True, gobject.PARAM_READWRITE),
    }

    def __init__(self, style):
        gtk.CellRendererText.__init__(self)
        self._active = True
        self._style = style


    def do_get_property(self, property):
        if property.name == 'active':
            return self._active
        else:
            raise AttributeError("unknown property {0}".format(property.name))


    def do_set_property(self, property, value):
        if property.name == 'active':
            self._active = value
            if self._active:
                self.props.foreground = self._style.text[gtk.STATE_NORMAL]
            else:
                self.props.foreground = self._style.text[gtk.STATE_INSENSITIVE]
        else:
            raise AttributeError("unknown property {0}".format(property.name))
