import gst

from AbstractCommand import *
from ElementData import *

class AddElementCommand(AbstractCommand):

    def __init__(self, pipeline, factory_name, element_name, x, y):
        AbstractCommand.__init__(self, pipeline)
        self._factory_name = factory_name
        self._element_name = element_name
        self._x = x
        self._y = y


    def do(self):
        elt = gst.element_factory_make(self._factory_name, self._element_name)
        data = ElementData(elt)
        data.x = self._x
        data.y = self._y
        self.pipeline.add(elt)
        # Use data.element to use the weak ref in the selection
        self.pipeline.plugster_selection.select(data.element)


    def undo(self):
        elt = self.pipeline.get_by_name(self._element_name)
        self.pipeline.plugster_selection.remove(elt)
        self.pipeline.remove(elt)
