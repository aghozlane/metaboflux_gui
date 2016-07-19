#!/usr/bin/python
# -*- coding: utf-8 -*-
from view import *
from gconfig import *
import gtk, gobject
import os

class GView(View):
    dir_glade = os.path.join(os.path.dirname(__file__))+os.sep+"glade"+os.sep
    
    window = None
    main_vbox = None
    container = None
    notebook = None
    popup_config = None

    def __init__(self):
        View.__init__(self)
        gtk.gdk.threads_init()
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.dir_glade+"main.glade")

        self.window = self.builder.get_object("window")
        dgd=gtk.gdk.display_get_default()
        gsd=dgd.get_default_screen()
        self.height = gsd.get_height()
        self.width = gsd.get_width()
        #self.window.resize(int(self.height * 1.2) , int(self.height * 0.85))
        self.main_vbox = self.builder.get_object("main_vbox")
        self.statusbar = self.builder.get_object("statusbar")
        self.about = self.builder.get_object("about")
        self.builder.connect_signals(self)
        
        self.window.show_all()

    def set_project(self):
        View.set_project(self)

        self.notebook = gtk.Notebook()
        self.notebook.set_scrollable(True)
        
        self.main_vbox.pack_start(self.notebook)
        self.main_vbox.reorder_child(self.notebook, 2)
        self.notebook.show_all()

    def run(self):
        View.run(self)
        gtk.main()

    def exit_main(self, widget = None):

        ask = gtk.MessageDialog(self.window,
                                gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_INFO,
                                gtk.BUTTONS_YES_NO,
                                """Do you really want to quit MetaBoFlux ?\n\nNote: remember that simulations are already saved on your hard drive.""")
        rep = ask.run()
        if rep == gtk.RESPONSE_YES:
            ask.destroy()
            View.exit_main(self)
            gtk.main_quit()
        else:
            ask.destroy()
            return

    def on_delete_event(self, widget, event):
        self.exit_main()
        return True

    def disp_about(self, widget):
        g = gtk.Builder()
        g.add_from_file(self.dir_glade+"about.glade")

        about = g.get_object("about")
        about.run()

        about.destroy()
        
        
    ###########################
    ##  Configuration popup  ##
    ## > added in July, 2010 ##
    ###########################
      
    def disp_popup_config(self,widget):
        """
        Displays the Configuration popup
        """
        # Popup structure/object
        self.builder.add_from_file(self.dir_glade+"popup_config.glade")
        self.popup_config = self.builder.get_object("popup_config")
        self.builder.connect_signals(self)
        
        # Configuration object + fill forms
        gconfig = GConfig(self.popup_config)
        gconfig.get_config_from_file(0)
        #gconfig.fill_table()
        gconfig.fill_tables()
        self.popup_config.show_all()
        
        
    def hide_popup_config(self,widget):
        """
        Hides the Configuration popup
        """
        self.popup_config.destroy()
        
        
    def save_config (self,widget):
        """
        Save the new configuration
        """
        gconfig = GConfig(self.popup_config)
        gconfig.save_config_from_popup(self.popup_config)
        
    
    def reset_config (self,widget):
        """
        Restore default configuration
        """
        gconfig = GConfig(self.popup_config)
        gconfig.restore_default_config(self.popup_config)
        self.popup_config.show_all()
        
        