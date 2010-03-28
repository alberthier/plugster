import gobject
import gtk

class PropertyEditorCellRenderer(gtk.GenericCellRenderer):

    __gsignals__ = {
        # edited signal: (path, new_value)
        'edited': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING)),
    }

    __gproperties__ = {
        'property-param-spec' : (gobject.TYPE_PYOBJECT, "Property ParamSpec", "The ParamSpec of the property to edit", gobject.PARAM_READWRITE),
        'property-value'      : (gobject.TYPE_PYOBJECT, "Property value", "The current value of the property to edit", gobject.PARAM_READWRITE),
    }


    def __init__(self):
        gtk.GenericCellRenderer.__init__(self)
        self.reset()


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
        else:
            raise AttributeError("unknown property {0}".format(property.name))


    def reset(self):
        self.props.mode = gtk.CELL_RENDERER_MODE_EDITABLE
        self._property_param_spec = None
        self._property_value = None
        self._renderers = {}


    def on_get_size(self, widget, cell_area):
        return self._get_current_renderer(widget).get_size(widget, cell_area)


    def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
        return self._get_current_renderer(widget).render(window, widget, background_area, cell_area, expose_area, flags)


    def on_activate(self, event, widget, path, background_area, cell_area, flags):
        return self._get_current_renderer(widget).activate(event, widget, path, background_area, cell_area, flags)


    def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
        return self._get_current_renderer(widget).start_editing(event, widget, path, background_area, cell_area, flags)


    def _get_current_renderer(self, widget):
        pspec = self.props.property_param_spec
        renderer = None
        if pspec in self._renderers:
            renderer = self._renderers[pspec]
        editable = pspec.flags & gobject.PARAM_WRITABLE == gobject.PARAM_WRITABLE
        editable = editable and not pspec.flags & gobject.PARAM_CONSTRUCT_ONLY == gobject.PARAM_CONSTRUCT_ONLY

        if pspec.value_type == gobject.TYPE_CHAR or \
           pspec.value_type == gobject.TYPE_UCHAR or \
           pspec.value_type == gobject.TYPE_INT or \
           pspec.value_type == gobject.TYPE_UINT or \
           pspec.value_type == gobject.TYPE_LONG or \
           pspec.value_type == gobject.TYPE_ULONG or \
           pspec.value_type == gobject.TYPE_INT64 or \
           pspec.value_type == gobject.TYPE_UINT64:
            if renderer == None:
                renderer = self._create_renderer_spin(widget, 0, editable, pspec.minimum, pspec.maximum)
            self._update_renderer_spin_value(renderer)
        elif pspec.value_type == gobject.TYPE_FLOAT or \
             pspec.value_type == gobject.TYPE_DOUBLE:
            if renderer == None:
                renderer = self._create_renderer_spin(widget, 2, editable, pspec.minimum, pspec.maximum)
            self._update_renderer_spin_value(renderer)
        elif pspec.value_type == gobject.TYPE_BOOLEAN:
            if renderer == None:
                renderer = self._create_renderer_bool(widget, editable)
            self._update_renderer_bool_value(renderer)
        elif pspec.value_type == gobject.TYPE_STRING:
            if renderer == None:
                renderer = self._create_renderer_text(widget, editable)
            self._update_renderer_text_value(renderer)
        elif pspec.value_type.is_a(gobject.TYPE_ENUM) and editable:
            if renderer == None:
                renderer = self._create_renderer_combo(widget, pspec.enum_class)
            self._update_renderer_combo_value(renderer, pspec.enum_class)
        elif pspec.value_type.is_a(gobject.TYPE_FLAGS):
            print("No renderer implemented for '{0}'".format(pspec))
            if renderer == None:
                renderer = self._create_renderer_text(widget, False)
            self._update_renderer_text_value(renderer)
        else:
            if renderer == None:
                renderer = self._create_renderer_text(widget, editable)
            self._update_renderer_text_value(renderer)

        self._renderers[pspec] = renderer
        return renderer;


    def _create_renderer_spin(self, widget, digits, editable, lower, upper):
        renderer = gtk.CellRendererSpin()
        renderer.connect('edited', self._on_renderer_value_changed)
        if not editable:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_INSENSITIVE]
        else:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_NORMAL]
        renderer.props.adjustment = gtk.Adjustment(value = 0, lower = lower, upper = upper, step_incr = 1, page_incr = 10, page_size = 0)
        renderer.props.digits = digits
        renderer.props.editable = editable
        return renderer


    def _update_renderer_spin_value(self, renderer):
        val = self.props.property_value
        if val != None:
            if isinstance(val, float):
                val = "{0:.2f}".format(val)
            else:
                val = str(val)
            renderer.props.text = val
        else:
            renderer.props.text = "---"


    def _create_renderer_bool(self, widget, editable):
        renderer = gtk.CellRendererCombo()
        renderer.connect('edited', self._on_renderer_value_changed)
        if not editable:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_INSENSITIVE]
        else:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_NORMAL]
        store = gtk.ListStore(gobject.TYPE_STRING)
        renderer.props.text_column = 0
        renderer.props.has_entry = False
        renderer.props.editable = True
        iter = store.append()
        store.set(iter, 0, "Yes")
        iter = store.append()
        store.set(iter, 0, "No")
        renderer.props.model = store
        return renderer


    def _update_renderer_bool_value(self, renderer):
        val = self.props.property_value
        if isinstance(val, bool):
            if val:
                renderer.props.text = "Yes"
            else:
                renderer.props.text = "No"
        else:
            renderer.props.text = "---"


    def _create_renderer_combo(self, widget, enum_class):
        renderer = gtk.CellRendererCombo()
        renderer.connect('edited', self._on_renderer_value_changed)
        store = gtk.ListStore(gobject.TYPE_STRING)
        renderer.props.model = store
        renderer.props.text_column = 0
        renderer.props.has_entry = False
        renderer.props.editable = True
        for (index, enum_item) in enum_class.__enum_values__.iteritems():
            iter = store.append()
            store.set(iter, 0, enum_item.value_nick)
        return renderer


    def _update_renderer_combo_value(self, renderer, enum_class):
        val = self.props.property_value
        if isinstance(val, int) and val >= 0 and val < len(enum_class.__enum_values__):
            renderer.props.text = enum_class.__enum_values__[val].value_nick
        else:
            renderer.props.text = "---"


    def _create_renderer_text(self, widget, editable):
        renderer = gtk.CellRendererText()
        renderer.connect('edited', self._on_renderer_value_changed)
        if not editable:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_INSENSITIVE]
        else:
            renderer.props.foreground = widget.get_style().text[gtk.STATE_NORMAL]
        renderer.props.editable = editable
        return renderer


    def _update_renderer_text_value(self, renderer):
        val = self.props.property_value
        if val != None:
            renderer.props.text = str(val)
        else:
            renderer.props.text = "---"


    def _on_renderer_value_changed(self, renderer, path, new_text):
        self.emit('edited', path, new_text)
