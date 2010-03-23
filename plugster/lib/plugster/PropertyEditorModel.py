import gobject
import gtk

class PropertyEditorModel(gtk.GenericTreeModel):

    # Columns
    PROPERTY_NAME_COLUMN       = 0
    PROPERTY_PARAM_SPEC_COLUMN = 1
    PROPERTY_VALUE_COLUMN      = 2
    NB_COLUMNS                 = 3

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
                for pspec in obj.__class__.props:
                    if not pspec in self.param_specs:
                        self.param_specs.remove(pspec)

        self.param_specs.sort(lambda a, b: a.nick < b.nick)
        for index, pspec in enumerate(self.param_specs):
            path = ( index, )
            self.row_inserted(path, self.get_iter(path))


    def set_property_value(self, path, new_text):
        iter = get_iter(path)
        pspec = iter.user_data
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
        elif pspec.value_type == gobject.TYPE_BOOL:
            val = new_text == "Yes"
        elif pspec.value_type == gobject.TYPE_ENUM:
            for enum_item in pspec.enum_class.__enum_values__:
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
            return gobject.TYPE_PARAM
        elif index == PropertyEditorModel.PROPERTY_VALUE_COLUMN:
            return gobject.TYPE_PYOBJECT
        else:
            return gobject.TYPE_INVALID


    def on_get_iter(self, path):
        if len(path) == 1 and path[0] < len(self.param_specs):
            return self.create_tree_iter(path[0])
        else:
            ##raise ValueError("{path} is not a valid tree path".format(path = path))
            return None


    def on_get_path(self, iter):
        return ( self.get_user_data(iter), )


    def on_get_value(self, iter, column):
        index = self.get_user_data(iter)
        if index >= 0 and index < len(self.param_specs):
            pspec = self.param_specs[index]
            if column == PropertyEditorModel.PROPERTY_NAME_COLUMN:
                return pspec.name
            elif column == PropertyEditorModel.PROPERTY_PARAM_SPEC_COLUMN:
                return pspec
            elif column == PropertyEditorModel.PROPERTY_VALUE_COLUMN:
                return self._get_objects_value(pspec.name)
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
