#!/usr/bin/python
# -*- coding: utf-8 -*-

from gui.gtk.ggraph import *
from result import *

import os, glob, re, csv
import copy, gobject, shutil, pango

class GResult(Result):
    """Send simulation results"""
    
    def __init__(self, sbml, graph, dir_result, dir_log,
                 dir_graphs, dir_glade, model, config, param):
        
        self.config = config
        self.dir_glade = dir_glade
        self.model = model
        self.dir_log = dir_log
        Result.__init__(self, sbml, graph, dir_result, dir_log, dir_graphs, config, param)
        
        
        if not self.new_flux or not self.histo or not self.log:
            self.valid = False
        else:
            self.valid = True

    def display_result(self, container_param, container_graph, container):
        """
        Display widgets with results : histo and graphs
        """

        # Display histo first and log
        builder = gtk.Builder()
        builder.add_from_file(self.dir_glade+"results.glade")
        self.frame = builder.get_object("results_frame")
        results_tab =  builder.get_object("results_tab")
        log_container = builder.get_object("log_container")
        group_log_container = builder.get_object("group_log_container")
        results_event = builder.get_object("results_event")
        results_event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
        results_event.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("gray"))

        # Set size of miniature
        self.w = self.h = container_param.get_allocation()[3]
        if self.w == 1:
            self.w = self.h = 600
        self.factor = 0.35

        self.histo_widget = []
            
        for i in self.histo:
            box, image = self.create_image(i)
            self.histo_widget.append(image)
            results_tab.pack_start(box, expand = False, fill = False)

        # Make label
        l = gtk.Label("<span foreground=\"blue\"><b>Results</b></span>")
        l.set_use_markup(True)
        l.set_angle(270)
        
        container_param.append_page(self.frame, l)
        container_param.set_current_page(5)
        container_param.show_all()

        # Add log widget
        log_container.add(self.get_log_widget(self.log))
        log_container.show_all()
        
        #Add group log widget
        group_log_container.add(self.get_log_widget(self.group_log))
        group_log_container.show_all()
        
        # Create graph results dir if necessary
        if not os.path.isdir(self.dir_graphs):
            os.makedirs(self.dir_graphs)
        
        # Display new graph widget
        for i in range(len(self.new_flux)):
            for k,v in self.new_flux[i].iteritems():
                g = GGraph(self.sbml, self.dir_graphs, self.config)
                g.image_name = g.image_name[:-4]+"-"+k+g.image_name[-4:]
                self.graphs.append(g)
    
                g.gen_graph(self.sbml.get_clean_flux(v),
                            self.model.graph.nodes_reac,
                            self.gp_final_amount[i][k]) # Processed new final amount (result.py)
                g.render(g.image_name)
                gobject.timeout_add(300, self.model.disp_graph, g, True)

    def create_image(self, img):
        pixbuf = gtk.gdk.pixbuf_new_from_file(img)
        scaled_buf = pixbuf.scale_simple(int(self.w * self.factor),
                                              int(self.h * self.factor),
                                              gtk.gdk.INTERP_BILINEAR)
        image = gtk.Image()
        image.set_from_pixbuf(scaled_buf)
        box = gtk.EventBox()
        box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
        box.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("gray"))
        box.add(image)
        box.connect("button_press_event", self.open_popup, pixbuf, img)

        return box, image

    def regen_histo(self):
        for widget, img in zip(self.histo_widget, self.histo):
            pixbuf = gtk.gdk.pixbuf_new_from_file(img)
            scaled_buf = pixbuf.scale_simple(int(self.w * self.factor),
                                             int(self.h * self.factor),
                                             gtk.gdk.INTERP_BILINEAR)
            
            widget.set_from_pixbuf(scaled_buf)

    def get_log_widget(self,log_file):
        """
        Create gtktreeview and set log in
        @param log_file Log file to table
        """
        ncols = len(log_file[0])
        ncols += 1
            
        log_model = gtk.ListStore(*([str] * ncols))

        # Create treeview with correct headers
        log_view = gtk.TreeView(log_model)
        
        for i, h in enumerate(['']+log_file[0]):
            # Create celle renderer
            renderer = gtk.CellRendererText()
            renderer.set_property('editable', False)
            renderer.set_property('alignment', pango.ALIGN_CENTER)
            renderer.set_property("xalign", 0.5)

            # Create column and add it to view
            col = gtk.TreeViewColumn(h, renderer, text = i)
            log_view.append_column(col)

        # Fill row
        for i, l in enumerate(log_file[1:]):
            t = [str(i+1)]+l
            log_model.append(t)

        return log_view

    def open_popup(self, widget, event, pixbuf=None,
                   image = None, disp = True):
        """
        Open popup with one histogram
        """

        if disp and event.button == 1: # Left click
            # Image creation
            pixbuf = gtk.gdk.pixbuf_new_from_file(image)
            view = piv.ImageView()
            view.set_pixbuf(pixbuf)
            scroll = piv.ImageScrollWin(view)
            view.connect("button_press_event",
                         self.open_popup,
                         pixbuf,
                         image,
                         False)

            h = pixbuf.get_height()
            w = pixbuf.get_width()

            # Window Creation
            win = gtk.Window()
            win.set_title("Result of MetaBoFlux")
            win.set_default_size(600, 400)
            win.add(scroll)

            win.show_all()

        elif event.button == 3: # Right click
            menu = gtk.Menu()
            item = gtk.ImageMenuItem(gtk.STOCK_SAVE)
            item.connect("activate",
                         self.model.save_graph,
                         os.path.basename(image),
                         image)
            item.show()
            menu.append(item)
            menu.popup(None,None,None,event.button,event.time)

    def clean_results(self):
        """
        Delete all widgets and objects related to results
        """

        # Delete widget
        for i in range(len(self.graphs)):
            self.model.note_graph.remove_page( \
                self.model.note_graph.page_num(self.graphs[0].scrollWinImage))
            del self.graphs[0]

        self.model.param.note_para.remove_page( \
            self.model.param.note_para.page_num(self.frame))

        self.histo[:] = []
        del self.frame

        # Delete all directories
        shutil.rmtree(self.model.simu.dir_simu+self.model.simu.result_dir_simu)
        shutil.rmtree(self.model.simu.dir_simu+self.model.simu.result_dir_stat)
        shutil.rmtree(self.model.simu.dir_simu+self.model.simu.result_dir_mini)
        shutil.rmtree(self.dir_graphs)
        