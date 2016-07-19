#!/usr/bin/python
# -*- coding: utf-8 -*-

from sbml import *
from graph import *
from gvgen import *
try:
    import gtkimageview as piv
except ImportError:
    import _gtkimageview as piv

import tempfile
import gtk, time, gobject
import os

class GGraph(Graph):
    """
    Class which handle with graphs generation according to an sbml object
    """

    def __init__(self, sbml, path, config, graph_file = None):
        Graph.__init__(self, sbml, path, config, graph_file)

        self.img = None
        self.scrollWinImage = None

        # Creating waiting widget
        label_processing = gtk.Label("Graph is processing . . .")
        anim_processing = gtk.gdk.PixbufAnimation(os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+".."+os.sep+"img"+os.sep+"waiting.gif")
        image_processing = gtk.Image()
        image_processing.set_from_animation(anim_processing)
        box_processing = gtk.VBox(spacing=10)
        box_processing.pack_start(label_processing,
                                  fill = False,
                                  expand = False)
        box_processing.pack_start(image_processing,
                                  fill = False,
                                  expand = False)
        
        self.widget_processing = gtk.Alignment(0.5,0.5)
        self.widget_processing.add(box_processing)

        self.previousObj = self.widget_processing
        self.oldPos = -1
        self.zoom = None

    def render(self, name = None):
        Graph.render(self, name)
        gobject.timeout_add(200, self.get_graph)

    def get_graph(self):
        """ Return graph widget """
        
        # If graph render is done, we create the widget
        if self.proc.poll() == 0:
            self.generate = True
            self.img_path = os.path.abspath(self.img_path)
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.img_path)
            if not self.img and not self.scrollWinImage: 
                self.img = piv.ImageView()
                self.scrollWinImage = piv.ImageScrollWin(self.img)
            self.img.set_pixbuf(pixbuf)
            if self.zoom:
                self.img.set_zoom(self.zoom)
            return False

        # If is done but the render return some errors
        # We launch other generation
        elif self.proc.poll() > 0 and self.proc.poll() != None:
            del self.graph
            self.gen_graph()
            self.render()
            return True

        # This mean multiple generation call
        else:
            return True
        
