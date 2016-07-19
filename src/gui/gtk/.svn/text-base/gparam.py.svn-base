#!/usr/bin/python
# -*- coding: utf-8 -*-

from param import *
from equation import *

from lxml import etree
import re, shutil, gtk
import sys, gobject, pango
import operator

class GParam(Param):
    """
    \brief Management settings glycoflux in xml format
    """

    def __init__(self, location, xml_file, dir_glade,
                 model, sbml, config, open_simu = False):
        """
        Tree init with \a default values

        @param test
        @return test
        """
        Param.__init__(self, location, xml_file, sbml, config, open_simu)

        self.note_para = None

        self.dir_glade = dir_glade
        self.model = model
        self.sbml = sbml
        self.is_load = False

        if self.is_valid:
            self.init()
        
    def init(self):

        self.is_load = True

        self.note_para = gtk.Notebook()
        self.note_para.set_tab_pos(gtk.POS_RIGHT)
        self.note_para.set_scrollable(True)

        # Init and fill widgets
        self.init_parameters_tab()

        self.init_values()
        self.fill_values()
        self.values_tab.show_all()
        
        self.init_species_tab()
        self.fill_species()
        self.species_frame.show_all()

        self.init_reactions_tab()
        self.fill_reactions()
        self.reactions_frame.show_all()

        self.init_equations_tab()
        self.fill_equations_tab()
        self.math_frame.show_all()

        self.init_representations()
        self.fill_representations()
        self.reset_representations()
        self.representations_frame.show_all()

    ###################################
    # Getters / Setters to param file #
    ###################################

    ##############################
    # Handle with paramaters tab #
    ##############################

    def init_parameters_tab(self):
        self.builder = {}
        self.tab = ["species","math","reactions","values", "representations"]
        for t in self.tab:
            self.builder[t] = gtk.Builder()

        self.builder["species"].add_from_file(self.dir_glade+"species.glade")
        self.builder["math"].add_from_file(self.dir_glade+"math.glade")
        self.builder["reactions"].add_from_file(\
            self.dir_glade+"reactions.glade")
        self.builder["values"].add_from_file(self.dir_glade+"values.glade")
        self.builder["representations"].add_from_file(\
            self.dir_glade+"representations.glade")

        # Connect signals
        for t in self.tab:
            self.builder[t].connect_signals(self)

        # Get object from glade file
        self.species_tab = self.builder["species"].get_object("species_tab")
        self.species_frame = self.builder["species"].get_object("species_frame")
        self.math_frame = self.builder["math"].get_object("math_frame")
        self.eq_box = self.builder["math"].get_object("equations_box")
        self.container_combo_math = self.builder["math"].get_object("container_combo_math")
        self.reactions_tab = self.builder["reactions"].get_object(\
            "reactions_tab")
        self.reactions_frame = self.builder["reactions"].get_object(\
            "reactions_frame")
        self.values_tab = self.builder["values"].get_object("values_frame")
        self.representations_frame = self.builder["representations"].\
                                     get_object("representations_frame")
        self.regen_button = self.builder["representations"].\
                                     get_object("gen_histo")
        self.regen_button.set_sensitive(False)
        self.list_core = self.builder["values"].get_object("list_proc")
        
        # Turn label to 270ￂﾰ
        label = []
        label.append(gtk.Label("Values"))
        label.append(gtk.Label("Species"))
        label.append(gtk.Label("Reactions"))
        label.append(gtk.Label("Equations"))
        label.append(gtk.Label("Representations"))
        for l in label:
            l.set_angle(270)
        
        self.note_para.append_page(self.values_tab, label[0])
        self.note_para.append_page(self.species_frame, label[1])
        self.note_para.append_page(self.reactions_frame, label[2])
        self.note_para.append_page(self.math_frame, label[3])
        self.note_para.append_page(self.representations_frame, label[4])

    #########################
    # Handle with value tab #
    #########################

    def init_values(self):
        proc = detectCPUs() + 1
        for i in range(2,proc+1):
            self.list_core.append([i])
    
    def get_values_tab(self, widget = None, event = None):
        for k,v in self.entry.iteritems():
            if widget == v[1]:
                
                if k == "nb_core":
                    core = None
                    if widget.get_active_text() == "default":
                        core = "0"
                    else:
                        core = widget.get_active_text()
                    self.set_values(k, core)
                else:
                    valid, err = self.set_values(k, widget.get_text())
                    if not valid:
                        value = self.values[k]
                        widget.set_text(value) # Put back the old value
                        self.model.disp_message("This value is wrong : " + err)
                    else:
                        if k == 'name':
                            self.model.change_tab_label(widget.get_text())
                        self.fill_representations()
                        self.model.disp_message("Value is ok")
                    
    def fill_values(self, widget = None):

        values = self.values
        if widget:
            values = self.old_values

        self.entry = { "name"           : ["entry_name"],
                       "nb_core"        : ["entry_core"],
                       "nbtriesMod"    : ["entry_nb_tries_mod"],
                       "nbSimulations"  : ["entry_nb_simu"],
                       "nbtriesSa"     : ["entry_nb_tries_sa"],
                       "nbiters"        : ["entry_nb_ite"],
                       "stepsize"       : ["entry_max_step"],
                       "Tinitial"       : ["entry_temp"],
                       "muT"            : ["entry_muT"],
                       "Tmin"           : ["entry_min_temp"],
                       "boltzmann"      : ["entry_boltz"],
                       "nbGroup"        : ["entry_group"],
                       "groupSize"      : ["entry_energy"],
                       "interestEnergy" : ["entry_best_energy"]
                     }

        for k, v in self.entry.iteritems():
            obj = self.builder["values"].get_object(v[0])
            if k == "nb_core":
                pass #obj.set_text(str(self.nb_core))
            else:
                obj.set_text(values[k])
            self.entry[k].append(obj)
        self.model.change_tab_label(self.values['name'])
            
    def clear_fill_values(self, widget = None):
        for k, v in self.entry.iteritems():
            if k == "name":
                v[1].set_text("")
                self.model.change_tab_label('-- No name set --')
            elif k == "nb_core":
                pass
            else:
                v[1].set_text("0")

    ###########################
    # Handle with Species tab #
    ###########################
    
    def init_species_tab(self):
        self.store_species = gtk.ListStore(gobject.TYPE_BOOLEAN,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_UINT,
                                           gobject.TYPE_BOOLEAN,
                                           gobject.TYPE_UINT,
                                           gobject.TYPE_UINT)
        self.store_species.filter_new()
        
        self.view_species = gtk.TreeView(self.store_species)
        self.view_species.set_enable_search(True)
        self.view_species.set_search_column(1)

        # FinalAmount CellRenderer
        renderer1 = gtk.CellRendererText()
        renderer1.set_property('editable', True)
        renderer1.set_property('alignment', pango.ALIGN_CENTER)
        renderer1.set_property("xalign", 0.5)
        renderer1.connect( 'edited', self.change_amount)

        # Species selection CellRenderer
        renderer2 = gtk.CellRendererToggle()
        renderer2.set_property('activatable', True)
        renderer2.connect( 'toggled', self.species_or_banned_selected, 0)
        
        # Species name CellRenderer
        renderer3 = gtk.CellRendererText()
        renderer3.set_property("xalign", 0.1)
        renderer3.set_property('alignment', pango.ALIGN_CENTER)
        
        # Banned selection CellRenderer
        renderer4 = gtk.CellRendererToggle()
        renderer4.set_property('activatable', True)
        renderer4.connect( 'toggled', self.species_or_banned_selected, 3)

        # InitialAmount CellRenderer
        renderer5 = gtk.CellRendererText()
        renderer5.set_property('editable', False)
        renderer5.set_property('alignment', pango.ALIGN_CENTER)
        renderer5.set_property("xalign", 0.5)

        # Ponderation CellRenderer
        self.renderer6 = gtk.CellRendererText()
        self.renderer6.set_property('editable', True)
        self.renderer6.set_property('alignment', pango.ALIGN_CENTER)
        self.renderer6.set_property("xalign", 0.5)
        self.renderer6.connect( 'edited', self.change_ponderation)

        # TreeViewColumn creations
        colonne0 = gtk.TreeViewColumn(None, renderer2)
        colonne0.add_attribute( renderer2, "active", 0)
        colonne1 = gtk.TreeViewColumn("Species", renderer3, text=1)
        colonne2 = gtk.TreeViewColumn("Final Amount", renderer1, text=2)
        colonne3 = gtk.TreeViewColumn(None, renderer4)
        colonne3.add_attribute( renderer4, "active", 3)
        colonne4 = gtk.TreeViewColumn("Initial\nAmount", renderer5, text=4)
        colonne5 = gtk.TreeViewColumn("Ponderation", self.renderer6, text=5)

        # Set column sortable
        colonne0.set_sort_column_id(0)
        colonne1.set_sort_column_id(1)
        colonne2.set_sort_column_id(2)
       
        # Create headers widgets
        headers_amount = gtk.Label("Final\nAmount")
        headers_amount.set_justify(gtk.JUSTIFY_CENTER)
        headers_amount.show()

        headers_banned = gtk.Label("Banned\ncompounds")
        headers_banned.set_justify(gtk.JUSTIFY_CENTER)
        headers_banned.show()

        headers_select = gtk.Label("Select\nspecies")
        headers_select.set_justify(gtk.JUSTIFY_CENTER)
        headers_select.show()

        headers_initial = gtk.Label("Initial\nAmount")
        headers_initial.set_justify(gtk.JUSTIFY_CENTER)
        headers_initial.show()

        headers_ponderation = gtk.Label("Ponderation")
        headers_ponderation.set_justify(gtk.JUSTIFY_CENTER)
        headers_ponderation.show()

        # Apply propertie to column
        colonne0.set_resizable(True)
        colonne1.set_resizable(True)
        colonne2.set_resizable(True)
        colonne3.set_resizable(True)
        
        colonne1.set_expand(True)
        colonne2.set_expand(False)
        colonne3.set_expand(False)

        colonne0.set_widget(headers_select)
        colonne2.set_widget(headers_amount)
        colonne3.set_widget(headers_banned)
        colonne4.set_widget(headers_initial)
        colonne5.set_widget(headers_ponderation)

        colonne2.set_alignment(0.5)
        colonne3.set_alignment(0.5)
        colonne4.set_alignment(0.5)
        colonne5.set_alignment(0.5)
                
        # Add column to the view
        self.view_species.append_column(colonne0)
        self.view_species.append_column(colonne1)
        self.view_species.append_column(colonne4)
        self.view_species.append_column(colonne2)
        self.view_species.append_column(colonne3)
        self.view_species.append_column(colonne5)
        
        self.species_tab.add_with_viewport(self.view_species)

    def fill_species(self, reset = False):

        if reset:
            self.species = self.old_species.copy()
            self.store_species.clear()
        
        for s in self.sbml.species:
            banned = False
            selected = False
            finalAmount = 0
            ponderation = 0
            name = self.sbml.get_name(s)
            
            if name in self.banned_compounds:
                banned = True
            if name in self.species.keys():
                selected = True
                finalAmount = self.species[name][0]
                if self.species[name][1]:
                    ponderation = self.species[name][1]
            initialAmount = self.sbml.get_initial_amount(name)

            # Update model
            self.store_species.append([selected, name, int(finalAmount),
                                       banned, int(initialAmount),
                                      int(ponderation)])

        rows = [tuple(r) + (i,) for i, r in enumerate(self.store_species)]
        rows.sort(key=operator.itemgetter(1))
        self.store_species.reorder([r[-1] for r in rows])
        
        if reset:
            self.model.update_graph()

    def change_amount( self, cellrenderer, path, new_texte):
        try:
            self.store_species[path][2] = int(new_texte)
        except:
            self.model.disp_message("Not a number.")
            return
        
        if self.store_species[path][2] != 0:
            self.store_species[path][0] = True
            if self.store_species[path][5] == 0:
                self.store_species[path][5] = 1
        else:
            self.store_species[path][0] = False
            self.store_species[path][5] = 0

        name = self.store_species[path][1]
        selected = self.store_species[path][0]
        amount = self.store_species[path][2]
        weight = self.store_species[path][5]
        
        self.send_change_amount(name, str(amount), selected, str(weight))

    def change_ponderation( self, cellrenderer, path, new_texte):
        if self.store_species[path][0]:
            try:
                self.store_species[path][5] =  int(new_texte)
            except:
                self.model.disp_message("Not a number.")
                return
            self.model.disp_message("Ponderation correct")
        else:
            self.model.disp_message("This species needs to be selected before to set a ponderation.")
            return

        name = self.store_species[path][1]
        selected = self.store_species[path][0]
        amount = self.store_species[path][2]
        weight = self.store_species[path][5]

        self.send_change_amount(name, str(amount), selected, str(weight))
        
    def species_or_banned_selected( self, cellrenderer, path, col):
        
        self.store_species[path][col] = not self.store_species[path][col]
        name = self.store_species[path][1]
        selected = self.store_species[path][col]

        # If banned compounds selected
        if col == 3:
            self.set_banned_compounds(name, not selected)
            self.model.update_graph()
        elif col == 0:
            if selected and self.store_species[path][5] == 0:
                self.store_species[path][5] = 1
            elif not selected:
                self.store_species[path][5] = 0
            amount = self.store_species[path][2]
            weight = self.store_species[path][5]
            self.send_change_amount(name, str(amount), selected, str(weight))

    def send_change_amount(self, name, fAmount, selected, weight):
        if selected == False:
            up = self.set_species(name, fAmount, weight, delete = True)
        else:
            up = self.set_species(name, fAmount, weight)

        # If parameters changed : update graph
        if up:
            self.model.update_graph()

    def reset_defaults_species(self, widget):
        """
        Reset widget species according
        to default settings loaded at startup
        """
        self.fill_species(reset = True)

    ################################
    # Handle with banned compounds #
    ################################

    def set_banned_compounds(self, name, delete = False):
        """ Overwrite Param method to update store model in gtk side """
        Param.set_banned_compounds(self, name, delete)

        # Update gtk model store
        for i in range(len(self.store_species)):
            name = self.store_species[i][1]
            banned = not self.store_species[i][3]

            if banned and name in self.banned_compounds:
                self.store_species[i][3] = banned
                                   
    ############################
    # Handle with Reaction tab #
    ############################

    def init_reactions_tab(self):
        self.store_reactions = gtk.ListStore(gobject.TYPE_BOOLEAN,
                                             gobject.TYPE_STRING,
                                             gobject.TYPE_STRING)
        
        self.view_reactions = gtk.TreeView(self.store_reactions)
        self.view_reactions.set_property("enable-grid-lines", True)

        # FinalAmount CellRenderer
        renderer1 = gtk.CellRendererText()
        renderer1.set_property("xalign", 0.5)

        # Nodes selection CellRenderer
        renderer2 = gtk.CellRendererToggle()
        renderer2.set_property('activatable', True)
        renderer2.connect( 'toggled', self.node_selected, 0)
        
        # Species name CellRenderer
        renderer3 = gtk.CellRendererText()
        renderer3.set_property("xalign", 0.1)
        
        # TreeViewColumn creations
        colonne0 = gtk.TreeViewColumn(None, renderer2)
        colonne0.add_attribute( renderer2, "active", 0)
        colonne1 = gtk.TreeViewColumn("Reactions", renderer3, text=1)
        colonne2 = gtk.TreeViewColumn("Nodes Ref.", renderer1, text=2)

        # Create headers widgets
        headers_nodes = gtk.Label("Nodes\nRef.")
        headers_nodes.set_justify(gtk.JUSTIFY_CENTER)
        headers_nodes.show()

        headers_select = gtk.Label("Select\nreactions")
        headers_select.set_justify(gtk.JUSTIFY_CENTER)
        headers_select.show()

        colonne0.set_sort_column_id(0)

        # Apply propertie to column
        colonne0.set_resizable(True)
        colonne1.set_resizable(True)
        colonne2.set_resizable(True)

        colonne1.set_expand(True)
        colonne2.set_expand(False)

        colonne0.set_widget(headers_select)
        colonne2.set_widget(headers_nodes)

        colonne2.set_sort_column_id(2)
        colonne2.set_sort_order(gtk.SORT_ASCENDING)
        
        # Add column to the view
        self.view_reactions.append_column(colonne0)
        self.view_reactions.append_column(colonne1)
        #self.view_reactions.append_column(colonne2)

        self.reactions_tab.add_with_viewport(self.view_reactions)
        
    def fill_reactions(self):
        self.merge_reactions_group = self.sbml.get_nodes(\
            self.get_reactions_group())

        for ref, value in self.merge_reactions_group.iteritems():
            reac_str = ""
            for r in value:
                reac_str += str(r + "\n")
            reac_str = reac_str[:-1]

            is_checked = ref in self.get_reactions_group().keys()

            # Update model
            self.store_reactions.append([is_checked, reac_str, ref])

        rows = [tuple(r) + (i,) for i, r in enumerate(self.store_reactions)]
        rows.sort(key=operator.itemgetter(2))
        self.store_reactions.reorder([r[-1] for r in rows])

    def node_selected(self, cellrenderer, path, col):
        """
        This method is called when user check a reactions nodes
        """
        self.store_reactions[path][col] = not self.store_reactions[path][col]
        self.update_reactions_group_with_gtk_model(path)
        self.model.update_graph()

    def update_reactions_group_with_gtk_model(self, row):
        """
        Update internal model reaction_group
        with gtk.model
        """
        model = self.store_reactions
        delete = not model[row][0]
        node = model[row][2]
        reac_list = model[row][1].split('\n')

        self.set_reactions_group(node, reac_list, delete)
        
    ############################
    # Handle with equation tab #
    ############################

    def init_equations_tab(self):

        # Add combo box for reactions
        
        self.combo_math = gtk.ComboBox(self.get_liststore(self.sbml.reactions))
        cell = gtk.CellRendererText()
        self.combo_math.pack_start(cell, True)
        self.combo_math.add_attribute(cell, 'text', 0)
        self.container_combo_math.pack_start(gtk.Label("List of reactions :"))
        self.container_combo_math.pack_start(self.combo_math)
        
        self.combo_math.set_add_tearoffs(True)
        self.combo_math.set_title("List of reactions :")
        self.combo_math.connect("changed", self.math_button)

        # Add combo box for species
        self.combo_math2 = gtk.ComboBox(self.get_liststore(self.sbml.species))
        cell = gtk.CellRendererText()
        self.combo_math2.pack_start(cell, True)
        self.combo_math2.add_attribute(cell, 'text', 0)
        self.container_combo_math.pack_start(gtk.Label("List of species :"))
        self.container_combo_math.pack_start(self.combo_math2)
  
        self.combo_math2.set_add_tearoffs(True)
        self.combo_math.set_title("List of species :")
        self.combo_math2.connect("changed", self.math_button)

        # Connect buttons
        b1 = self.builder["math"].get_object("button1")
        b2 = self.builder["math"].get_object("button2")
        b3 = self.builder["math"].get_object("button3")
        b4 = self.builder["math"].get_object("button4")
        b5 = self.builder["math"].get_object("button5")
        b6 = self.builder["math"].get_object("button6")
        b7 = self.builder["math"].get_object("button7")
        b8 = self.builder["math"].get_object("button8")
        b9 = self.builder["math"].get_object("button9")
        b10 = self.builder["math"].get_object("button10")
        b1.connect("clicked", self.math_button, "+")
        b2.connect("clicked", self.math_button, "-")
        b3.connect("clicked", self.math_button, "*")
        b4.connect("clicked", self.math_button, "/")
        b5.connect("clicked", self.math_button, "=")
        b6.connect("clicked", self.math_button, ">")
        b7.connect("clicked", self.math_button, "<")
        b8.connect("clicked", self.math_button, ">=")
        b9.connect("clicked", self.math_button, "<=")
        b10.connect("clicked", self.math_button, "remove")
            
    def fill_equations_tab(self, reset = False):
        self.equ_list = []
        self.current_equation = None
        if reset:
            kinetic_law = self.old_kinetic_law
        else:
            kinetic_law = self.kinetic_law

        if not kinetic_law:
            self.add_equation_widget()
        else:
            for name, eq in kinetic_law.iteritems():
                # Create new widget equation
                self.add_equation_widget(equation = " ".join(eq), name = name)

    def add_equation_widget(self, widget = None, equation = "", name = None):
        tmp = Equation(self, equation, self.dir_glade,
                       name, self.sbml)
        tmp.set_equation(equation)
        self.equ_list.append(tmp)
        self.handle_radio(None, tmp)
        tmp.radio.connect("released", self.handle_radio, tmp)

    def remove_equation_widget(self, widget = None, object = None):
        self.eq_box.remove(object.equation)
        self.equ_list.remove(object)
        object.remove_equation()
        self.model.disp_message("Equation removed.")
        self.handle_radio(None, object, remove = True)

    def set_default_equation_tab(self, widget):
        i = 0
        while i < len(self.equ_list):
            self.remove_equation_widget(object = self.equ_list[i])
        
        self.fill_equations_tab(reset = True)

    def handle_radio(self, widget = None, equation = None, remove = False):
        """
        Handle with pseudo radio button
        """
        if remove and equation == self.current_equation:
            if not self.equ_list:
                self.current_equation = None
            else:
                self.current_equation = self.equ_list[0]
                self.equ_list[0].radio.set_active(True)
        else:
            previous = self.current_equation
            for e in self.equ_list:
                if e == equation:
                    e.radio.set_active(True)
                    self.current_equation = equation
                elif e == previous:
                    e.radio.set_active(False)

    def math_button(self, widget, op = None):
        if self.current_equation:
            if not op:
                text = widget.get_active_text()
                self.current_equation.add_sth(text)

                # Get species
                sp = []
                for i in self.sbml.species:
                    sp.append(self.sbml.get_name(i))
                # Get reactions
                reac = []
                for i in self.sbml.reactions:
                    reac.append(self.sbml.get_name(i))

                if text in reac:
                    self.combo_math.set_model(None)
                    self.combo_math.set_model(self.get_liststore(self.sbml.reactions))
                elif text in sp:
                    self.combo_math2.set_model(None)
                    self.combo_math2.set_model(self.get_liststore(self.sbml.species))
            else:
                self.current_equation.add_sth(op)   
        else:
            self.model.disp_message("There is no equations.")

    def get_liststore(self, list):
        box = gtk.ListStore(gobject.TYPE_STRING)
        tmp = []
        for r in list:
            tmp.append(self.sbml.get_name(r))
        tmp.sort()
        for r in tmp:
            box.append([r])
        return box
         
    ##################################
    # Handle with representation tab #
    ##################################

    def init_representations(self):
        """
        Initialisation of representations widgets
        """
        self.rep = []
        self.rep.append(self.builder["representations"].get_object("align_ref1"))
        self.rep.append(self.builder["representations"].get_object("align_ref2"))
        self.rep.append(self.builder["representations"].get_object("align_ref3"))
        self.rep.append(self.builder["representations"].get_object("align_ref4"))
        self.rep.append(self.builder["representations"].get_object("align_ref5"))

    def fill_representations(self, reset = False):
        """
        Fill representations widget with param values
        """
        self.rep_object = {}
        for i in range(len(self.rep)):
            r, table = self.create_table_repr(\
                self.get_representation()[str(i)], self.rep[i], i, reset)
            self.rep_object[i] = [r, table]
            
    def create_table_repr(self, values, container, pos, reset):
        """
        Create table widget which fill it with representations values.
        """
        
        if container.get_children():
            container.get_children()[0].destroy()
        
        builder = gtk.Builder()
        builder.add_from_file(self.dir_glade+"rep_table.glade")
        builder.connect_signals(self)
        table = builder.get_object("table")
        if reset:
            rep = self.old_representation
        else:
            rep = self.get_representation()

        entry = {"title" : None,
                 "subtitle" : None,
                 "xtext" : None,
                 "ytext" : None,
                 "height" : None,
                 "width" : None}
        for label in entry:
            entry[label] = builder.get_object(label)
            string = rep[str(pos)][label]
            entry[label].set_text(string)

        container.add(table)
        return entry, table

    def reset_representations(self, widget = None):
        """
        Reset representations widget
        """
        self.fill_representations(reset = True)
        for k,v in self.rep_object.iteritems():
            for l, w in v[0].iteritems():
                self.update_representations(w)

    def update_representations(self, widget, event = None):
        """
        Update representations
        """
        # Double iteration to find what representation part has been
        # modified
        for k,v in self.rep_object.iteritems():
            if v[1] == widget.get_parent():
                for l, w in v[0].iteritems():
                    if w == widget:
                        self.set_representation(str(k), l,
                                                widget.get_text(),
                                                debug=True)
            
    def show_info_representations(self, widget):
        builder = gtk.Builder()
        builder.add_from_file(self.dir_glade+"help_representations.glade")

        help_dialog = builder.get_object("help_representations_dialog")
        help_dialog.run()
        help_dialog.destroy()

    def regenerate_histo(self, widget):
        self.model.launch_simu(regen = True)

    def check_number(self, widget, key):
        """
        Check if key pressed is a number
        """
        # 65288 : backspace
        # 65293 : enter
        # 65289 : tab
        if re.match("[0-9]", key.string) or key.keyval in (65288, 65293, 65289):
            return False
        else:
            self.model.disp_message("Only numeric character is allowed.")
            return True
    
    ##########################################################
    # Check if there is enough param to launch simulation    #
    ##########################################################
    def check_param(self):
        """
        Check if there is enough param to launch simulation
        """
        
        if not self.species:
            self.errors_check = "You have to select at least one species."
            return False
        elif not self.reactions_group:
            self.errors_check = "You have to select at least one reactions node."
            return False
        
        return True

def detectCPUs():
  """
  Detects the number of CPUs on a system. Cribbed from pp.
  """
  # Linux, Unix and MacOS: # Linux, Unix et MacOS:
  if hasattr (os, "sysconf" ):
    if os . sysconf_names . has_key( "SC_NPROCESSORS_ONLN" ):
      # Linux & Unix: # Linux et Unix:
      ncpus = os . sysconf( "SC_NPROCESSORS_ONLN" )
      if isinstance (ncpus, int ) and ncpus > 0 :
          return ncpus 
      else : # OSX:
          return int (os . popen2( "sysctl -n hw.ncpu" )[ 1 ] . read())
    # Windows:
  if os . environ . has_key( "NUMBER_OF_PROCESSORS" ):
    ncpus = int (os . environ[ "NUMBER_OF_PROCESSORS" ]);
    if ncpus > 0 :
      return ncpus
  return 1 # Default 1 
