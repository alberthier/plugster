import weakref

import gobject
import gst

from ElementData import *

class Selection(gobject.GObject):

    __gsignals__ = {
        'selection-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }


    def __init__(self, pipeline):
        gobject.GObject.__init__(self)
        self._pipeline = weakref.proxy(pipeline)
        self.selected_elements = []
        self._pipeline.plugster_selection = self
        self._pipeline.connect('element-removed', self._on_element_removed)


    def add(self, element):
        if not element in self.selected_elements:
            self.selected_elements.append(element)
            element.plugster_data.emit('selected-state-changed')
            self.emit('selection-changed')


    def remove(self, element):
        if element in self.selected_elements:
            self.selected_elements.remove(element)
            element.plugster_data.emit('selected-state-changed')
            self.emit('selection-changed')


    def clear(self):
        previously_selected_elements = self.selected_elements
        self.selected_elements = []
        for element in previously_selected_elements:
            element.plugster_data.emit('selected-state-changed')
        self.emit('selection-changed')


    def select(self, element):
        self.clear()
        self.add(element)


    def toggle(self, element):
        if element in self.selected_elements:
            self.remove(element)
        else:
            self.add(element)


    def contains(self, element):
        return element in self.selected_elements


    def _on_element_removed(self, pipeline, element):
        self.remove(element)
