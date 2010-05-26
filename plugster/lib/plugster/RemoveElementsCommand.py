import gst

from AbstractCommand import *

class RemoveElementsCommand(AbstractCommand):

    def __init__(self, pipeline, elements):
        AbstractCommand.__init__(self, pipeline)
        self._elements_info = []
        for elt in elements:
            info = {}
            info['factory_name'] = elt.get_factory().get_name()
            info['element_name'] = elt.get_name()
            info['x'] = elt.plugster_data.x
            info['y'] = elt.plugster_data.y
            self._elements_info.append(info)


    def do(self):
        for info in self._elements_info:
            elt = self.pipeline.get_by_name(info['element_name'])
            self.pipeline.plugster_selection.remove(elt)
            self.pipeline.remove(elt)


    def undo(self):
        for info in self._elements_info:
            elt = gst.element_factory_make(info['factory_name'], info['element_name'])
            data = ElementData(elt)
            data.x = info['x']
            data.y = info['y']
            self.pipeline.add(elt)
            # Use data.element to use the weak ref in the selection
            self.pipeline.plugster_selection.select(data.element)
