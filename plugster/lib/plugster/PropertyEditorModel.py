import glib
import gobject
import gtk

class PropertyEditorModel(gtk.GenericTreeModel):

    # Columns
    PROPERTY_NAME_COLUMN       = 0
    PROPERTY_PARAM_SPEC_COLUMN = 1
    PROPERTY_VALUE_COLUMN      = 2
    TOOLTIP_COLUMN             = 3
    NB_COLUMNS                 = 4

    def __init__(self):
        gtk.GenericTreeModel.__init__(self)
        self.objects = []
        self.param_specs = []


    def set_objects(self, objects):
        index = len(self.param_specs)
        for param_spec in reversed(self.param_specs):
            index -= 1
            self.row_deleted(( index, ))

        self.objects = objects
        first = True
        self.param_specs = []
        for obj in self.objects:
            if first:
                first = False
                self.param_specs = list(obj.__class__.props)
            else:
                toremove = []
                for pspec in self.param_specs:
                    if not pspec in obj.__class__.props:
                        toremove.append(pspec)
                for pspec in toremove:
                    self.param_specs.remove(pspec)

        for index, pspec in enumerate(self.param_specs):
            path = ( index, )
            self.row_inserted(path, self.get_iter(path))


    def set_property_value(self, path, new_text):
        iter = self.get_iter(path)
        pspec = self.get_value(iter, PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN)
        if pspec.value_type == gobject.TYPE_CHAR or \
           pspec.value_type == gobject.TYPE_UCHAR or \
           pspec.value_type == gobject.TYPE_INT or \
           pspec.value_type == gobject.TYPE_UINT or \
           pspec.value_type == gobject.TYPE_LONG or \
           pspec.value_type == gobject.TYPE_ULONG:
            val = int(new_text)
        elif pspec.value_type == gobject.TYPE_INT64 or \
           pspec.value_type == gobject.TYPE_UINT64:
            val = long(new_text)
        elif pspec.value_type == gobject.TYPE_FLOAT or \
           pspec.value_type == gobject.TYPE_DOUBLE:
            val = float(new_text)
        elif pspec.value_type == gobject.TYPE_BOOLEAN:
            val = new_text == "Yes"
        elif pspec.value_type == gobject.TYPE_ENUM:
            for (index, enum_item) in pspec.enum_class.__enum_values__.iteritems():
                if new_text == enum_item.value_nick:
                    val = enum_item
                    break
        else:
            val = new_text

        for obj in self.objects:
            obj.set_property(pspec.name, val)

        self.row_changed(path, iter)


    def on_get_flags(self):
        return gtk.TREE_MODEL_ITERS_PERSIST | gtk.TREE_MODEL_LIST_ONLY


    def on_get_n_columns(self):
        return PropertyEditorModel.NB_COLUMNS


    def on_get_column_type(self, index):
        if index == PropertyEditorModel.PROPERTY_NAME_COLUMN:
            return gobject.TYPE_STRING
        elif index == PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN:
            return gobject.TYPE_PYOBJECT
        elif index == PropertyEditorModel.PROPERTY_VALUE_COLUMN:
            return gobject.TYPE_PYOBJECT
        elif index == PropertyEditorModel.TOOLTIP_COLUMN:
            return gobject.TYPE_STRING
        else:
            return gobject.TYPE_INVALID


    def on_get_iter(self, path):
        if len(path) == 1 and path[0] < len(self.param_specs):
            return self.create_tree_iter(path[0])
        else:
            return None


    def on_get_path(self, iter):
        return ( self.get_user_data(iter), )


    def on_get_value(self, iter, column):
        index = self.get_user_data(iter)
        if index >= 0 and index < len(self.param_specs):
            pspec = self.param_specs[index]
            if column == PropertyEditorModel.PROPERTY_NAME_COLUMN:
                if (len(pspec.nick) == 0):
                    prop_name = pspec.name
                else:
                    prop_name = pspec.nick
                val = self._get_objects_value(pspec)
                if val == None or pspec.default_value != val:
                    return "<b>{0}</b>".format(prop_name)
                else:
                    return prop_name
            elif column == PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN:
                return pspec
            elif column == PropertyEditorModel.PROPERTY_VALUE_COLUMN:
                return self._get_objects_value(pspec)
            elif column == PropertyEditorModel.TOOLTIP_COLUMN:
                flags = ""
                if pspec.flags & gobject.PARAM_READABLE:
                    flags += "Readable"
                if pspec.flags & gobject.PARAM_WRITABLE:
                    if pspec.flags & gobject.PARAM_READABLE:
                        flags += ", "
                    flags += "Writable"
                return "<b>{nick}</b> ({name})\n<b>Flags:</b> {flags}\n<b>Default value:</b> {defval}\n{desc}".format(nick = glib.markup_escape_text(pspec.nick),
                                                                                                                      name = glib.markup_escape_text(pspec.name),
                                                                                                                      flags = glib.markup_escape_text(flags),
                                                                                                                      defval = glib.markup_escape_text(str(pspec.default_value)),
                                                                                                                      desc = glib.markup_escape_text(pspec.blurb))
        return None


    def on_iter_next(self, iter):
        if iter:
            index = self.get_user_data(iter)
            if index >= 0 and index < len(self.param_specs) - 1:
                return self.create_tree_iter(index + 1)
            else:
                return None
        else:
            return self.create_tree_iter(0)


    def on_iter_children(self, parent):
        if not parent:
            if (len(self.param_specs) != 0):
                return self.create_tree_iter(0)
            else:
                return None
        else:
            return None


    def on_iter_has_child(self, iter):
        return False


    def on_iter_n_children(self, iter):
        if not iter:
            return len(self.param_specs)
        else:
            return 0


    def on_iter_nth_child(self, parent, n):
        if not parent and n >= 0 and n < len(self.param_specs):
            return self.create_tree_iter(n)
        else:
            return None


    def on_iter_parent(self, child):
        return None


    def _get_objects_value(self, param_spec):
        val = None
        if param_spec.flags & gobject.PARAM_READABLE:
            first = True
            for obj in self.objects:
                if first:
                    first = False
                    val = obj.get_property(param_spec.name)
                else:
                    tmp_val = obj.get_property(param_spec.name)
                    if val != tmp_val:
                        val = None
                        break
        return val
