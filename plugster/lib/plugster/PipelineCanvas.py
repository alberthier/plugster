import math

import gtk
import goocanvas

from ElementFactoriesWidget import *

class PipelineCanvas(goocanvas.Canvas):

    GRID_SIZE = 20.0

    def __init__(self):
        goocanvas.Canvas.__init__(self, has_tooltip = True,
                                        automatic_bounds = True,
                                        integer_layout = True)
        self.drag_dest_set(gtk.DEST_DEFAULT_ALL, ElementFactoriesWidget.DRAG_TARGETS, gtk.gdk.ACTION_COPY)
        self.props.automatic_bounds = True
        self.props.integer_layout = True

    @staticmethod
    def place_coord_on_grid(coord):
        delta = math.fmod(coord, PipelineCanvas.GRID_SIZE)
        if delta < PipelineCanvas.GRID_SIZE / 2.0:
            return int(-delta)
        else:
            return int(PipelineCanvas.GRID_SIZE - delta)
