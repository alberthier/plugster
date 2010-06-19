import gst

from AbstractCommand import *

class UnlinkPadsCommand(AbstractCommand):

    def __init__(self, pipeline, src_elt_name, src_pad_name, sink_elt_name, sink_pad_name):
        AbstractCommand.__init__(self, pipeline)
        self._src_elt_name = src_elt_name
        self._src_pad_name = src_pad_name
        self._sink_elt_name = sink_elt_name
        self._sink_pad_name = sink_pad_name


    def do(self):
        src_elt = self.pipeline.get_by_name(self._src_elt_name)
        sink_elt = self.pipeline.get_by_name(self._sink_elt_name)
        src_elt.unlink_pads(self._src_pad_name, sink_elt, self._sink_pad_name)


    def undo(self):
        src_elt = self.pipeline.get_by_name(self._src_elt_name)
        sink_elt = self.pipeline.get_by_name(self._sink_elt_name)
        src_elt.link_pads(self._src_pad_name, sink_elt, self._sink_pad_name)
