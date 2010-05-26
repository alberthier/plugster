import gobject
import gst

from AbstractCommand import *

class SetPropertyCommand(AbstractCommand):

    def __init__(self, pipeline, elements, property_param_spec, property_value):
        AbstractCommand.__init__(self, pipeline)
        self._element_names = []
        self._old_values = []
        for elt in elements:
            self._element_names.append(elt.get_name())
            self._old_values.append(None)
        self._property_param_spec = property_param_spec
        self._property_value = property_value


    def do(self):
        if self._property_param_spec.value_type.is_a(gobject.TYPE_FLAGS):
            for (elt_index, elt_name) in enumerate(self._element_names):
                elt = self.pipeline.get_by_name(elt_name)
                val = elt.get_property(self._property_param_spec.name)
                self._old_values[elt_index] = val
                for (index, (mask, flag)) in enumerate(self._property_param_spec.flags_class.__flags_values__.iteritems()):
                    if self._property_value[index] != None:
                        if self._property_value[index] == 0:
                            if val & mask == mask:
                                val -= mask
                        else:
                            if val & mask == 0:
                                val += mask
                elt.set_property(self._property_param_spec.name, val)
        else:
            for (elt_index, elt_name) in enumerate(self._element_names):
                elt = self.pipeline.get_by_name(elt_name)
                self._old_values[elt_index] = elt.get_property(self._property_param_spec.name)
                elt.set_property(self._property_param_spec.name, self._property_value)


    def undo(self):
        for (elt_index, elt_name) in enumerate(self._element_names):
            elt = self.pipeline.get_by_name(elt_name)
            elt.set_property(self._property_name, self._old_values[elt_index])
