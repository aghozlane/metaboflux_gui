#!/usr/bin/python
# -*- coding: utf-8 -*-

from gui.gtk.gmodel_simu import *
from gui.gtk.gview import *
from gui.gtk.gconfig import *
from view import *

import os

class App:
    """
    Main class which handle simulations tab and create main view object.
    This class can create, remove or open simulation.
    """
    
    def __init__(self, ui="GTK"):
        """
        Constructor : create one empty simulation tab by default with GTK view.
        Read json configuration file.

        @param ui view type (only GTK supported now)
        """
        
        ## Path to sbml file
        self.sbml_file = ""

        ## Path to configuration file
        self.path_config = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+"config.metabo"
        
        ## List of models object
        self.models = {}

        ## Reference to current view
        self.view = None

        ## Current foreground simulation (reference to his page
        ## number)
        self.page = 0

        # Load config
        self.config=""
        try:
            f = open(self.path_config, "r")
            ## App configuration
            self.config = json.load(f)
            f.close()
        except:
            sys.exit("Error with file: %s"%self.path_config)

        # Convert unicode -> str
        for k, v in self.config.iteritems():
            self.config[k] = str(v)

        ## Default directory to put simulation (tmp/)
        self.dir_app = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+self.config["workspace"]
        
        # Create workspace if does not exist
        if not os.path.isdir(self.dir_app):
            os.makedirs(self.dir_app)

        # Create one model and put it in models list according to ui
        if ui == "GTK":
            ## View object
            self.view = GView()
            self.view.set_project()
            model = GModelSimu(self.view,
                               self.dir_app,
                               self,
                               self.page,
                               self.sbml_file,
                               self.config)
            self.view.notebook.connect("switch-page", self.change_page)
            #model.edit_conf() # Fill the configuration popup
        else:
            print "Sorry, this UI doesnt exist yet !"
        
        # Set models in model lists
        self.models[self.page] = model

        # Connect action
        self.connect_action()

        # Init get_object self.buttons
        ## All non simulation specific buttons
        self.buttons = []
        self.buttons.append(self.view.builder.get_object("export_config"))
        self.buttons.append(self.view.builder.get_object("export_results"))
        self.buttons.append(self.view.builder.get_object("import_sbml"))
        self.buttons.append(self.view.builder.get_object("import_config"))
        self.buttons.append(self.view.builder.get_object("start_action"))
        self.buttons.append(self.view.builder.get_object("stop_action"))
        self.buttons.append(self.view.builder.get_object("erase_previous_simu_action"))
        
    def run(self):
        """
        Run the main loop
        """
        self.view.run()

    def connect_action(self):
        """
        Connect various buttons from the view to app
        """
        ## Reference to button 'new'
        self.new_action = self.view.builder.get_object("new")
        ## Reference to button 'open'
        self.open_action = self.view.builder.get_object("open")
         
        self.new_action.connect("activate", self.add_model)
        self.open_action.connect("activate", self.select_model)

    def add_model(self, widget=None, dir_simu=None):
        """
        Add new simulation tab.
        Add model object to models list.

        @param widget signal source
        @param dir_simu parent directory of the simulation
        @return model ref to simulation tab object
        """
        page = len(self.models)
        model = GModelSimu(self.view,
                           self.dir_app,
                           self,
                           page,
                           self.sbml_file,
                           self.config)

        self.models[page] = model
        self.view.notebook.set_current_page(page)
        model.set_sensitive()

        return model

    def select_model(self, widget):
        """
        Ask user directory name to open existant simulation.
        (gtk specific)

        @param widget signal source
        """
        chooser = gtk.FileChooserDialog(title=None,
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        chooser.set_current_folder(self.dir_app)
        if chooser.run() == gtk.RESPONSE_OK:
            dir = chooser.get_filename()
            chooser.destroy()
            self.open_model(dir)
        chooser.destroy()

    def open_model(self, dir_simu):
        """
        Open existant simulation from hard drive directory

        @param dir_simu directory of an existant simulation
        """
        # Check if simu is already loaded
        for k, v in self.models.iteritems():
            if os.path.basename(v.dir_simu) == os.path.basename(dir_simu):
                self.error_message("This simulation is already loaded.")
                return

        # Check if the is conf.metabo file
        if not os.path.isfile(dir_simu + os.sep+"config.metabo"):
            self.error_message("This directory does not seems to be a valid metaboflux simulation directory.")
            return
        
        # Load config file
        f = open(dir_simu + os.sep+"config.metabo", "r")
        config = json.load(f)
        f.close()

        # Treat config file
        step = -1
        for k, v in config.iteritems():

            # Unicode -> string conversion
            if not k == "simu_dir":
                config[k] = str(v)
            
            if k == "sbml_file" and v:
                if step < 1:
                    step == 1
                step = 1
            elif k == "param_file" and v:
                if step < 2:
                    step = 2
            elif k == "result" and v:
                if step < 3:
                    step = 3
        
        # Load adequat model
        model = self.add_model(config["graphs_dir"])
        model.init_model(config["sbml_file"], dir_simu, config["graph_file"])
        model.container.show_all()

        # Load param file
        if step == 2:
            model.init_param(config["param_file"], config["simu_dir"], True)
            model.container.show_all()

        # Load results
        if step == 3:
            model.init_param(config["param_file"], config["simu_dir"], True)
            dir_stat = model.dir_simu + config["simu_dir"]["stat"]
            dir_log = model.dir_simu + config["simu_dir"]["mini"]
            model.init_results(dir_stat, dir_log)
            model.container.show_all()

    def error_message(self, mess):
        """
        Display custom error message.
        (gtk specific)

        @param mess message to display
        """
        about = gtk.MessageDialog(self.view.window,
                                  gtk.DIALOG_MODAL,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  mess)
        about.run()
        about.destroy()
        
    def change_page(self, widget, point, page):
        """
        Change current simulation tab to an other.
        (gtk specific)

        @param widget signal source
        @param point
        @param page new simulation to display
        """
        ## Current number page
        self.current_page = page
        if len(self.models) > 0 and not page == -1:
            self.models[page].set_sensitive()

    def update_page(self, model):
        """
        Update page number of opened simulations when close a model
        tab.
        (gtk specific)

        @param model closed model
        """
        page = model.page
        model.page = -1
        del self.models[page]

        if len(self.models) > 0:
            for p in range(page + 1, len(self.models) + 1):
                self.models[p - 1] = self.models[p]
                del self.models[p]
                self.models[p - 1].page = p - 1

            self.models[self.view.notebook.get_current_page()].set_sensitive()

        if len(self.models) == 0:
            self.unsensitive_buttons()

    def unsensitive_buttons(self):
        """
        Set all buttons unsensitive.
        (gtk specific)
        """
        for b in self.buttons:
            b.set_sensitive(False)

        
