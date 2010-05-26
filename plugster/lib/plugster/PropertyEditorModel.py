import glib
import gobject
import gtk

class PropertyEditorModel(gtk.GenericTreeModel):

    # Columns
    PROPERTY_NAME_COLUMN       = 0
    PROPERTY_PARAM_SPEC_COLUMN = 1
    PROPERTY_VALUE_COLUMN      = 2
    TOOLTIP_COLUMN             = 3
    ACTIVE_COLUMN              = 4
    NB_COLUMNS                 = 5

    def __init__(self):
        gtk.GenericTreeModel.__init__(self)
        self._objects = []
        self._param_specs = []


    def set_objects(self, objects):
        index = len(self._param_specs)
        for param_spec in reversed(self._param_specs):
            index -= 1
            self.row_deleted(( index, ))

        self._objects = objects
        self._param_specs = []
        for inedx, obj in enumerate(self._objects):
            if index == 0:
                self._param_specs = list(obj.__class__.props)
            else:
                toremove = []
                for pspec in self._param_specs:
                    if not pspec in obj.__class__.props:
                        toremove.append(pspec)
                for pspec in toremove:
                    self._param_specs.remove(pspec)

        for index, pspec in enumerate(self._param_specs):
            path = ( index, )
            self.row_inserted(path, self.get_iter(path))


    def set_property_value(self, path, new_val):
        if len(self._objects) > 0:
            first_object = self._objects[0]
            pipeline_controller = first_object.plugster_data.get_pipeline().plugster_pipeline_controller

            iter = self.get_iter(path)
            pspec = self.get_value(iter, PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN)

            pipeline_controller.set_property(self._objects, pspec, new_val)

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
        elif index == PropertyEditorModel.ACTIVE_COLUMN:
            return gobject.TYPE_BOOLEAN
        else:
            return gobject.TYPE_INVALID


    def on_get_iter(self, path):
        if len(path) == 1 and path[0] < len(self._param_specs):
            return self.create_tree_iter(path[0])
        else:
            return None


    def on_get_path(self, iter):
        return ( self.get_user_data(iter), )


    def on_get_value(self, iter, column):
        index = self.get_user_data(iter)
        if index >= 0 and index < len(self._param_specs):
            pspec = self._param_specs[index]
            if column == PropertyEditorModel.PROPERTY_NAME_COLUMN:
                if (len(pspec.nick) == 0):
                    prop_name = pspec.name
                else:
                    prop_name = pspec.nick
                val = self._get_objects_value(pspec)
                if pspec.default_value != val:
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
                                                                                                                      defval = self._get_default_value(pspec),
                                                                                                                      desc = glib.markup_escape_text(pspec.blurb))
            elif column == PropertyEditorModel.ACTIVE_COLUMN:
                return self._is_param_spec_supported(pspec) and \
                       (pspec.flags & gobject.PARAM_WRITABLE == gobject.PARAM_WRITABLE) and \
                       (not pspec.flags & gobject.PARAM_CONSTRUCT_ONLY == gobject.PARAM_CONSTRUCT_ONLY)
        return None


    def _is_param_spec_supported(self, pspec):
        return pspec.value_type == gobject.TYPE_CHAR or \
               pspec.value_type == gobject.TYPE_UCHAR or \
               pspec.value_type == gobject.TYPE_INT or \
               pspec.value_type == gobject.TYPE_UINT or \
               pspec.value_type == gobject.TYPE_LONG or \
               pspec.value_type == gobject.TYPE_ULONG or \
               pspec.value_type == gobject.TYPE_INT64 or \
               pspec.value_type == gobject.TYPE_UINT64 or \
               pspec.value_type == gobject.TYPE_FLOAT or \
               pspec.value_type == gobject.TYPE_DOUBLE or \
               pspec.value_type == gobject.TYPE_BOOLEAN or \
               pspec.value_type == gobject.TYPE_STRING or \
               pspec.value_type.is_a(gobject.TYPE_ENUM) or \
               pspec.value_type.is_a(gobject.TYPE_FLAGS)


    def _get_default_value(self, pspec):
        if pspec.value_type.is_a(gobject.TYPE_ENUM):
            defval = pspec.default_value.value_nick
        elif pspec.value_type.is_a(gobject.TYPE_FLAGS):
            defval = " | ".join(pspec.default_value.value_names)
        else:
            defval = str(pspec.default_value)
        return glib.markup_escape_text(defval)


    def on_iter_next(self, iter):
        if iter != None:
            index = self.get_user_data(iter)
            if index >= 0 and index < len(self._param_specs) - 1:
                return self.create_tree_iter(index + 1)
            else:
                return None
        else:
            return self.create_tree_iter(0)


    def on_iter_children(self, parent):
        if parent == None:
            if (len(self._param_specs) != 0):
                return self.create_tree_iter(0)
            else:
                return None
        else:
            return None


    def on_iter_has_child(self, iter):
        return False


    def on_iter_n_children(self, iter):
        if iter == None:
            return len(self._param_specs)
        else:
            return 0


    def on_iter_nth_child(self, parent, n):
        if parent == None and n >= 0 and n < len(self._param_specs):
            return self.create_tree_iter(n)
        else:
            return None


    def on_iter_parent(self, child):
        return None


    def _get_objects_value(self, param_spec):
        val = None
        if param_spec.flags & gobject.PARAM_READABLE:
            if param_spec.value_type.is_a(gobject.TYPE_FLAGS):
                for index, obj in enumerate(self._objects):
                    if index == 0:
                        val = []
                        flags = obj.get_property(param_spec.name)
                        for mask, flag in param_spec.flags_class.__flags_values__.iteritems():
                            if flags & mask == mask:
                                val.append(flag)
                            else:
                                val.append(0)
                    else:
                        flags = obj.get_property(param_spec.name)
                        for index, (mask, flag) in enumerate(param_spec.flags_class.__flags_values__.iteritems()):
                            if not val[index] == None:
                                if flags & mask == mask and val[index] == 0:
                                    val[index] = None
                                elif flags & mask == 0 and val[index] != 0:
                                    val[index] = None
            else:
                for index, obj in enumerate(self._objects):
                    if index == 0:
                        val = obj.get_property(param_spec.name)
                    else:
                        tmp_val = obj.get_property(param_spec.name)
                        if val != tmp_val:
                            val = None
                            break
        return val
