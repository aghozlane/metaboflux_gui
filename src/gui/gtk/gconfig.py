#!/usr/bin/python
# -*- coding: utf-8 -*-

from gview import *
from gmodel_simu import *

from lxml import etree
import re, shutil, gtk
import sys, gobject, pango
import operator

class GConfig:
    """
    Manage the Configuration popup
    @attention: The graphic handling is managed by the GView class (disp_popup_config,hide_popup_config)
    @author: Laurent Gil
    """
    
    def __init__(self, popup):
        """
        Default values
        @param popup: GTK object (Window)
        """
        self.path_config = "..%sconfig.metabo"%os.sep
        self.path_config_default = "..%sconfig.metabo_default"%os.sep
        self.popup_config = popup
        self.config = None
        
        self.output = [ ['resu_stat', 'Statistical results','1'],
                        ['resu_simu', 'Simulation results', '1'],
                        ['resu_mini', 'Minimal results',    '1'],
                        ['dir_tmp', ' Temporary directory', '1'],
                       ]
        
        self.link = [ ['graphviz_binary', 'Graphviz binary','0'],
                      ['path_mpd',        'MPD path',       '1'],
                      ['path_metabo',     'metaboflux path','1'],
                      ['file_format',     'Image format',   '0'],
                    ]
       
        self.file = [ ['workspace',           'Workspace',              '0'],
                      ['name',                'Name file',              '0'],
                      ['progress',            'Progress file',          '0'],
                      ['path_schema_file',    'Schema file (XSD)',      '1'],
                      ['param_name',          'Parameters file',        '0'],
                      ['path_default_param',  'Default parameters file','1'],
                      ['graph_name',          'Graphic file',           '0'],
                      ['path_results_graphs', 'Graphic results',        '1'],
                    ]
        
        self.frames = [ ["Output repositories",self.output], ["Program links",self.link], ["Path files",self.file]]
        
        
    def get_config_from_file(self,type):
        # Load config
        if type==0:
            f = open(self.path_config, "r")
        else:
            f = open(self.path_config_default, "r")
        ## App configuration
        self.config = json.load(f)
        f.close()

        # Convert unicode -> str
        for k, v in self.config.iteritems():
            self.config[k] = str(v)
        
        
        
    def fill_tables(self):
        """
        Fill the fields in the configuration popup, for each table of the interface
        """
        vbox1 = self.popup_config.get_child()
        vbox1_children = vbox1.get_children()

        flabel=0
        for fn in self.frames:
            for frame in vbox1_children:
                if frame.get_label() == fn[0]:
                    tab = frame.get_child().get_child()
                    self.fill_a_table(tab,flabel)
                    flabel += 1
                    break
                
        #f1 = self.popup_config.get_internal_child(builder,"frame1")
        #print f1.get_label()
    
    def fill_a_table (self,tab,id):
        """
        Fill the fields in a given table
        """
        nb = 0
        tab_children = tab.get_children()
        for i in self.frames[id][1]:
            k = i[0]
            
          # LABEL
            kl = i[1]
            labelflag = 0
            # Edit existing label
            for child in tab_children:
                if child.get_name()== str(nb) and child.__class__.__name__=="Label":
                    child.set_text(kl+' :')
                    labelflag=1
                    break
            # Add Label
            if (not labelflag):
                label = gtk.Label()
                label.set_text(kl+' :')
                label.set_alignment(0.9,0.5)
                label.set_name(str(nb))
                tab.attach(label,0,1,nb,nb+1)
            
          # VALUES (input)  
            v = self.config[k]  
            inputflag = 0
            # Edit existing entry
            for child in tab_children:
                if child.get_name()== str(nb) and child.__class__.__name__=="Entry":
                    child.set_text(v)
                    inputflag=1
                    break
            # Add text inputs
            if (not inputflag):
                text_input = gtk.Entry()
                text_input.set_text(v)
                text_input.set_name(str(nb))
                tab.attach(text_input,1,2,nb,nb+1)
            nb += 1
            
    
    def empty_tables (self):
        """
        Empty the fields in the configuration popup
        """
        vbox1 = self.popup_config.get_child()
        vbox1_children = vbox1.get_children()

        for fn in self.frames:
            for frame in vbox1_children:
                if frame.get_label() == fn[0]:
                    tab = frame.get_child().get_child()
                    for tchild in tab.get_children():
                        tchild.set_text('')
                    break
      
      
    def save_config_from_popup(self,widget):
        """
        Get all the values from the Configuration popup forms.
        Write the new values into the config.metabo file.
        """
        vbox1 = self.popup_config.get_child()
        vbox1_children = vbox1.get_children()

        flabel=0
        count_frames = len(self.frames)
        content="{\n"
        # Browse each frame (table)
        for fn in self.frames:
            for frame in vbox1_children:
                if frame.get_label() == fn[0]:
                    tab = frame.get_child().get_child()
                    if (flabel == count_frames-1):
                        last = 1
                    else:
                        last = 0
                    # Get all the values from a given table
                    content += self.save_config_from_a_table(tab,flabel,last)
                    flabel += 1
                    break
        content += "}\n"
        # Write the new config.metabo content
        f = open(self.path_config, "w")
        f.write(content)
        f.close()
        widget.destroy()
        
                
    def save_config_from_a_table(self,tab,id,end):
        """
        Get all the values contained in a given table
        """
        tab_content = ''
        # Browse Table
        tab_children = tab.get_children()
        lentab = len(tab_children)/2
        # Check each label and entry, to fill the configuration file
        for i in range(lentab):
            for line in tab_children:
                current_row = self.frames[id][1][i] #id: frame; 1: 2nd entry in the "id" row; i: row in the array 
                if line.get_name() == str(i) and line.__class__.__name__=="Label" :
                    label = current_row[0]
                    
                if line.get_name() == str(i) and line.__class__.__name__=="Entry" :
                    entry = line.get_text()
            
            if (i==(lentab-1) and end!=0):
                comma=''
            else:
                comma=','
            tab_content += "\t"+'"'+label+'" : "'+entry+'"'+comma+"\n"
        return tab_content
           
           
    def restore_default_config(self,widget):
        """
        Replace the current configuration (config.metabo) by the default
        configuration (config.metabo_default) in the displayed popup
        """
        self.get_config_from_file(1)
        self.empty_tables()
        self.fill_tables()
        