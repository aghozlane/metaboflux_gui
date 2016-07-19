# -*- coding: utf-8 -*-

from gui.gtk.gparam import *
from gui.gtk.ggraph import *
from gui.gtk.gsimulation import *
from gui.gtk.gresult import *
from model_simu import *

import gtk, gobject, shutil, thread, pango,os

class GModelSimu(ModelSimu):
    
    def __init__(self, view,
                 parent_dir,
                 app,
                 page,
                 sbml_file,
                 config,
                 param_file = None,
                 dir_graphs = None):
        
        ModelSimu.__init__(self, view, parent_dir, sbml_file,
                           param_file, config, dir_graphs = None)

        self.config = config

        # Various attributs
        self.auto_save = None
        self.menu = None
        self.empty_simu = True
        self.progress = None

        # Some widget references
        self.status_bar = self.view.statusbar
        self.context = self.status_bar.get_context_id("context")

        self.label_load_sbml = gtk.Label("You have to import SBML file.")
        
        # Creating container
        self.container = gtk.HPaned()
        taille = self.view.height
        self.container.set_position(int(taille * 0.55))
        self.view.notebook.insert_page(self.label_load_sbml,
                                       self.create_close_button("No title"))

        # Init connection in menu toolbar
        self.page = page
        self.number = page
        self.app = app
        self.menubar_connect()
                                       
        self.disp_message("Welcome in MetaBoFlux.")
        self.view.notebook.show_all()

    ###############
    # Init method #
    ###############

    def init_model(self, sbml_file, dir_simu = None, graph_file = None):
        ModelSimu.init_model(self, sbml_file, dir_simu)

        # SBML log generation
        f = open(self.dir_simu+os.sep+"sbml_errors.log", "w")
        f.write(self.sbml.errors_message)
        f.close()

        # Check if sbml is valid
        if not self.sbml.valid:
            # Remove sbml file
            os.remove(self.sbml.sbml_file)

            # Display a errors message
            about = gtk.MessageDialog(self.view.window,
                                      gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_ERROR,
                                      gtk.BUTTONS_CLOSE,
                                      "SBML file : \"%s\" is not valid.\n Check sbml_errors.log to see details."% os.path.basename(self.sbml.sbml_file))

            about.run()
            about.destroy()
            return

        # Graph generation
        self.graph = GGraph(self.sbml, self.dir_simu, self.config, graph_file)
        self.graph.start()
        self.update_graph()
        self.update_conf("graph_file", os.path.basename(self.graph.image_name))

        # Add hpaned in notebook
        self.label_load_sbml.destroy()
        self.view.notebook.insert_page(self.container,
                                       self.create_close_button("No title"),
                                       self.page)
        
        # Insert graph widgets
        self.note_graph = gtk.Notebook()
        self.note_graph.set_scrollable(True)
    
        self.note_graph.set_tab_pos(gtk.POS_LEFT)
        
        self.container.add1(self.note_graph)

        self.default_label = gtk.Label("Graph")
        self.default_label.set_angle(90)        
        self.note_graph.append_page(self.graph.widget_processing,
                                    self.default_label)

        self.container.add2(self.ask_load_default)
        self.menu_import_config.set_sensitive(True)

        # Show container
        self.container.show_all()
        self.view.notebook.set_current_page(self.page)

    def init_param(self, param_file, result_dir = None, open_simu = False):
        """
        Init all param widgets
        """
        # Load param file
        self.param = GParam(self.dir_simu,
                            param_file,
                            self.view.dir_glade,
                            self, self.sbml,
                            self.config, open_simu)
        self.is_param = True
        self.update_conf("param_file", os.path.basename(self.param.location))

        if not self.param.is_valid:
            # Remove sbml file
            os.remove(self.param.location)

            # Display a errors message
            about = gtk.MessageDialog(self.view.window,
                                      gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_ERROR,
                                      gtk.BUTTONS_CLOSE,
                                      "Param file : \"%s\" is not valid"% os.path.basename(self.param.xml_file))

            about.run()
            about.destroy()
            return

        param_file = self.param.location
        
        self.change_tab_label(self.param.values["name"])
        
        # Set hypotetic banned compounds in param object
        for s in self.sbml.list_banned:
            self.param.set_banned_compounds(s)
        self.param.write()

        # Creating simulation instance
        self.simu = GSimulation(self,
                                self.sbml_file,
                                param_file,
                                self.dir_simu,
                                self.config,
                                result_dir)
        self.is_simu = True
        self.update_conf("simu_dir", {"stat" : self.simu.result_dir_stat,
                                      "mini" : self.simu.result_dir_mini,
                                      "simu" : self.simu.result_dir_simu})

        # Insert button to load default config
        self.ask_load_default.destroy()
        self.container.add2(self.param.note_para)

        self.start_action.set_sensitive(True)
        self.menu_export_config.set_sensitive(True)
        self.menu_import_config.set_sensitive(False)

        # Show container
        self.container.show_all()

        self.update_graph()
        self.empty_simu = False

        # Auto save param.xml every 1 min
        self.auto_save = gobject.timeout_add(60000, self.auto_save_param)

        self.param.reset_representations()

    def auto_save_param(self):
        """
        Save param.xml file
        """
        self.param.write()
        self.disp_message("Param file was successfully auto saved.")

    def menubar_connect(self):
        """
        Connect menu signal with method
        """

        # Various widgets
        b = gtk.Builder()
        b.add_from_file(self.view.dir_glade+"ask_load.glade")
        self.ask_load_default = b.get_object("ask_load_default")
        
        # Get menu object and / or buttons
        self.menu_export_config = self.view.builder.get_object("export_config")
        self.export_results_action = self.view.builder.get_object("export_results")
        self.menu_import_sbml = self.view.builder.get_object("import_sbml")
        self.menu_import_config = self.view.builder.get_object("import_config")
        self.start_action = self.view.builder.get_object("start_action")
        self.stop_action = self.view.builder.get_object("stop_action")
        self.erase_simu = self.view.builder.get_object("erase_previous_simu_action")
        self.load_default = b.get_object("load_default")
        self.load_custom = b.get_object("load_custom")

        # Connect menu
        self.menu_export_config.connect("activate", self.export_config)
        self.export_results_action.connect("activate", self.export_results)
        self.menu_import_sbml.connect("activate", self.import_sbml)
        self.menu_import_config.connect("activate", self.import_config, True)
        self.start_action.connect("activate", self.launch_simu)
        self.stop_action.connect("activate", self.stop_simulation)
        self.erase_simu.connect("activate", self.erase_previous_results)
        
        self.load_default.connect("clicked", self.import_config, False)
        self.load_custom.connect("clicked", self.import_config, True)

    def set_sensitive(self):
        """
        Set sensitive or not each button according to current model
        """

        # Set import sbml and export simu button
        if self.is_sbml and self.sbml.is_load:
            self.export_results_action.set_sensitive(True)
            self.menu_import_sbml.set_sensitive(False)
        else:
            self.menu_import_sbml.set_sensitive(True)
            self.export_results_action.set_sensitive(False)

        # Set import config button
        if self.is_param and self.param.is_load or not self.is_sbml:
            self.menu_import_config.set_sensitive(False)
        else:
            self.menu_import_config.set_sensitive(True)

        # Set export config button
        if self.is_sbml and self.is_param:
            self.menu_export_config.set_sensitive(True)
        else:
            self.menu_export_config.set_sensitive(False)

        # Set start, stop, erase results buttons

        if self.is_resu and self.resu.valid:
            self.erase_simu.set_sensitive(True)
            self.param.regen_button.set_sensitive(True)
        else:
            self.erase_simu.set_sensitive(False)
            if self.is_param:
                self.param.regen_button.set_sensitive(False)

        if self.is_sbml and self.is_param and self.is_simu and not self.simu.state:
            self.start_action.set_sensitive(True)
            self.stop_action.set_sensitive(False)
        else:
            self.start_action.set_sensitive(False)
            if self.is_simu and self.simu.state:
                self.stop_action.set_sensitive(True)
            else:
                self.stop_action.set_sensitive(False)

    def import_sbml(self, widget):
        """
        Import sbml file and init the model
        """

        if not self.page == self.app.current_page:
            return

        chooser = gtk.FileChooserDialog("Import SBML file...",
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_current_folder(self.parent_dir)

        action = chooser.run()
        if action == gtk.RESPONSE_OK:
            f = chooser.get_filename()
            chooser.destroy()
            self.init_model(f)
        else:
            chooser.destroy()
            return

    def import_config(self, widget, custom):
        """
        Import sbml file and init the model
        """

        if not self.page == self.app.current_page:
            return
        
        f = self.default_param_file
        if custom:
            chooser = gtk.FileChooserDialog("Import config file...",
                                            None,
                                            gtk.FILE_CHOOSER_ACTION_OPEN,
                                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            chooser.set_default_response(gtk.RESPONSE_OK)
            chooser.set_current_folder(self.parent_dir)

            action = chooser.run()
            if action == gtk.RESPONSE_OK:
                f = chooser.get_filename()
                chooser.destroy()
            else:
                chooser.destroy()
                return

        self.init_param(f)

    ###########################
    # Handle with graph event #
    ###########################

    def update_graph(self):
        """ Update graph according to changeset in param object """

        finalAmount = None
        nodes_reac = {}
        if self.is_param:
            finalAmount = self.param.species
            nodes_reac = self.param.get_reactions_group()
        
            # Update banned compounds in sbml object
            self.sbml.list = []
            for s in self.param.banned_compounds:
                self.sbml.set_banned_compounds(s)

        if self.graph.img:
            self.graph.zoom = self.graph.img.get_zoom()

        self.graph.gen_graph(finalAmount = finalAmount, nodes_reac = nodes_reac)
        self.graph.render()
        gobject.timeout_add(400, self.disp_graph)

    def disp_graph(self, graph = None, color = False):
        # Display widgets

        if graph == None:
            graph = self.graph

        title = graph.image_name
        if color:
            title = "<span foreground=\"blue\"><b>"+ \
                    graph.image_name  +"</b></span>"

        label = gtk.Label(title)
        label.set_use_markup(True)
        label.set_angle(90)
        
        obj = None
        add = False
        
        if graph.generate:
            obj = graph.scrollWinImage
            obj.connect("button_press_event", self.popup_save_image)
            value = False
            add = True
        elif not graph.generate and graph.widget_processing in \
                 self.note_graph.get_children():
            add = False
            value = True
        else:
            obj = graph.widget_processing
            value = True
            add = True

        if add:
            if graph.previousObj in self.note_graph.get_children():
                self.note_graph.remove(graph.previousObj)
            graph.previousObj = obj
        
            self.note_graph.append_page(obj, tab_label=label)
            if graph.oldPos < 0:
                graph.oldPos = self.note_graph.get_n_pages()
            self.note_graph.reorder_child(obj, graph.oldPos-1)
            self.note_graph.set_current_page(graph.oldPos-1)
            self.note_graph.show_all()
        
        return value

    ####################
    # Simulation event #
    ####################

    def erase_previous_results(self, widget = None):
        """
        Erase results of previous simulations
        """

        if not self.page == self.app.current_page:
            return
        
        ask = gtk.MessageDialog(self.view.window,
                                    gtk.DIALOG_MODAL,
                                    gtk.MESSAGE_INFO,
                                    gtk.BUTTONS_YES_NO,
                                    """Do you really want to erase\
                                    previous simulation results ?""")
        rep = ask.run()
        if rep == gtk.RESPONSE_YES:
            ask.destroy()
            self.resu.clean_results()
            del self.resu
            self.update_conf("result", False)
            self.is_resu = False
            if self.progress:
                self.progress.destroy()
            self.set_sensitive()
            return True
        else:
            ask.destroy()
            return False

    def launch_simu(self, widget = None, regen = False):
        """
        Launch simulation
        """
        self.disp_message("Start simulation.")
        if not self.page == self.app.current_page:
            return

        # Ask if user really want to erase previous simulation
        if not regen and self.is_resu and self.resu.valid:
            if not self.erase_previous_results():
                return

        # Check if all param are valid
        if not self.param.check_param():
            ask = gtk.MessageDialog(self.view.window,
                                    gtk.DIALOG_MODAL,
                                    gtk.MESSAGE_WARNING,
                                    gtk.BUTTONS_CANCEL,
                                    self.param.errors_check)
            rep = ask.run()
            ask.destroy()
            return
            
        # Progress bar
        
        self.progress = gtk.ProgressBar()
        if regen:
            text  ="Regeneration is processing ..."
            self.progress.set_text(text)
        self.progress.set_pulse_step(0.2)
        self.view.statusbar.pack_start(self.progress,
                                       expand = True,
                                       fill = True)
        self.progress.show()
                
        # Launch simulation
        self.simu.stop = False
        self.simu.state = True
        self.param.write()
        
        code = self.simu.launch(self.param.nb_core, regen)
        self.set_sensitive()

    def stop_simulation(self, widget):
        """
        Stop current simulation
        """

        if not self.page == self.app.current_page:
            return
        
        self.simu.stop = True
        self.simu.state = False
        
        self.progress.destroy()
        self.disp_message("Simulation was stopped.")
        self.set_sensitive()
        
    def simu_is_done(self, result_dir_stat,
                     result_dir_log, regen = False):
        """
        Create new result object which offers all simulation results
        """
        self.progress.destroy()
        self.view.notebook.set_current_page(self.page)

        if self.simu.return_code != 1:
            text = "Simulation is done."
            if regen and not self.simu.stop:
                text = "Histograms regeneration is done."
            self.disp_message(text)

            if not regen:
                # Create result object
                self.init_results(result_dir_stat, result_dir_log)
            else:
                self.resu.regen_histo()
        else:
            if regen:
                text = "Regeneration failed."
            else:
                text = "Simulation finished with errors : look log_simu.txt"
                #self.simu.remove_dir()
            self.disp_message(text)
        
        self.set_sensitive()

    def init_results(self, dir_stat, dir_log):
        self.resu = GResult(self.sbml,
                            self.graph,
                            dir_stat,
                            dir_log,
                            self.dir_simu+self.dir_graphs,
                            self.view.dir_glade,
                            self,
                            self.config, 
                            self.param)
        self.is_resu = True
        self.update_conf("result", True)

        if self.resu.valid:
            self.resu.display_result(self.param.note_para,
                                     self.note_graph,
                                     self.container)
        else:
            #self.simu.remove_dir()
            self.disp_message("Results does not seems to be valid: look log_simu.txt")

        self.set_sensitive()

    ##########################
    # Save and export method #
    ##########################

    def popup_save_image(self, widget, event):
        """ Save image """

        if event.button == 3: # Right click
            self.menu = gtk.Menu()
            item = gtk.ImageMenuItem(gtk.STOCK_SAVE)
            item.connect("activate",self.save_graph)
            self.menu.append(item)
            self.menu.popup(None,None,None,event.button,event.time)
            self.menu.show_all()

    def save_graph(self, widget = None, image_name = None, image = None):
        """
        Save graph on file
        """
        widget.destroy()
        if not image:
            image = self.graph.img_path
        if not image_name:
            image_name = self.graph.image_name

        self.save_file(None, None,
                       self.dir_simu,
                       image_name,
                       image)

    def export_config(self, widget):
        """
        Export configuration file
        """
        
        if not self.page == self.app.current_page:
            return
        
        if not self.empty_simu:
            self.param.write()
            self.save_file(None, None,
                           self.dir_simu,
                           self.param.param_xml,
                           self.param.location)

    def export_results(self, widget):
        """
        Export results
        """

        if not self.page == self.app.current_page:
            return
        
        chooser = gtk.FileChooserDialog(title=None,
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_SAVE_AS,gtk.RESPONSE_OK))
        chooser.set_current_folder(os.path.expanduser('~'))
        if chooser.run() == gtk.RESPONSE_OK:
            dir = chooser.get_filename()
            dest = dir+"/"+os.path.basename(self.dir_simu)
            shutil.copytree(self.dir_simu, dest)
            self.disp_message("Results has been saved at "+dest)
            self.set_sensitive()
        chooser.destroy()
        

    ######################################
    # Standard method and usefull method #
    ######################################

    def close_model(self, widget):
        """
        Close model
        """

        self.view.notebook.set_current_page(self.page)

        direct = False
        ask = None
        if self.is_sbml:
            b = gtk.Builder()
            b.add_from_file(self.view.dir_glade+"ask_close.glade")
            ask = b.get_object("ask_close")
            rep = ask.run()
        else:
            direct = True

        if direct or rep == 1:
            if self.is_sbml:
                ask.destroy()
            if self.is_param:
                self.param.write()
            self.view.notebook.remove_page(self.page)
            if self.auto_save:
                gobject.source_remove(self.auto_save)
            self.app.update_page(self)

        elif rep == 2:
            ask.destroy()
            self.view.notebook.remove_page(self.page)
            if self.auto_save:
                gobject.source_remove(self.auto_save)
            shutil.rmtree(self.dir_simu)
            self.app.update_page(self)
        else:
            if self.is_sbml:
                ask.destroy()
            return
   
    def create_close_button(self, title):
        """
        Return a tab label widget with a close button
        """
        
        #hbox will be used to store a label and button, as notebook tab title
        hbox = gtk.HBox(False, 0)
        label = gtk.Label(title)
        hbox.pack_start(label)

        #get a stock close button image
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE,
                                               gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        
        #make the close button
        btn = gtk.Button()
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_focus_on_click(False)
        btn.add(close_image)
        hbox.pack_start(btn, False, False)
        btn.connect('clicked', self.close_model)
        
        #this reduces the size of the button
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        btn.modify_style(style)

        hbox.show_all()
        return hbox

    def change_tab_label(self, name):
        """
        Set a new name to the tab label of the current simu
        """
        self.view.notebook.set_tab_label(self.container,
                                         self.create_close_button(name))

    def disp_message(self, mess):
        """
        Display message in status bar
        """
        return self.status_bar.push(self.context, mess)

    def save_file(self,
                  widget,
                  event,
                  current_folder,
                  current_name,
                  source_file):
        """
        Method which save a file on hard drive
        and display a beautifull message when its done
        """
        
        chooser = gtk.FileChooserDialog(title=None,
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_SAVE_AS,gtk.RESPONSE_OK))
        chooser.set_current_folder(current_folder)
        chooser.set_current_name(current_name)
        if chooser.run() == gtk.RESPONSE_OK:
            img_file = chooser.get_filename()
            shutil.copy2(source_file, img_file)
            self.disp_message("File has been saved at "+img_file)
        chooser.destroy()
        