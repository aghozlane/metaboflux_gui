#!/usr/bin/python
# -*- coding: utf-8 -*-

from sbml import *
from param import *
from graph import *
from simulation import *
from result import *

import time, json, os

class ModelSimu:
    """
    ModelSimu class handle all steps to configure, launch and get
    results for one simulation.
    """
    
    def __init__(self,
                 view,
                 parent_dir,
                 sbml_file,
                 param_file=None,
                 config=None,
                 dir_graphs=None):

        """
        Various attributes initialisation.

        @param view view object
        @param parent_dir parent simulation directory
        @param sbml_file full path to the sbml file
        @param param_file path to the param file
        @param config dict which contains app configuration
        @param dir_graphs Path to directory of new graphs results
        """

        # Load config variable
        if not param_file:
            ## Default param file 
            #TODO a tester
            self.default_param_file = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+config["path_default_param"]

        ## Path to directory of new graphs results
        self.dir_graphs = config["path_results_graphs"]
        ## Name of the simulation configuration file (not param file)
        self.conf_file = os.sep+"config.metabo"

        ## View object
        self.view = view
        ## path to the param file
        self.param_file = param_file
        ## Parent simulation directory
        self.parent_dir = parent_dir
        ## Name of the simulation directory
        self.dir_simu = ""

        if dir_graphs:
            self.dir_graphs = dir_graphs

        ## Sbml is loaded
        self.is_sbml = False
        ## Param is loaded
        self.is_param = False
        ## Results are loaded
        self.is_resu = False
        ## Simulation is loaded
        self.is_simu = False

    def init_model(self, sbml_file, dir_simu=None):
        """
        Load sbml file and set new simulation directory (name is automatic).

        @param sbml_file full path to the sbml file
        @param dir_simu full path to the parent directory results
        """

        if not dir_simu:
            # Creation of directory
            name = time.strftime("%Y%m%d_%H-%M") + "_simulation"
            self.dir_simu = self.parent_dir + name

            # Mini iteration to avoid same directory problems
            i = 2
            out = False
            while not out:
                if os.path.isdir(self.dir_simu):
                    if i > 2:
                        self.dir_simu = self.dir_simu[:-2] + "-" + str(i)
                    else:
                        self.dir_simu = self.dir_simu + "-" + str(i)
                else:
                    out = True
                i += 1
            os.makedirs(self.dir_simu)
            shutil.copy2(sbml_file, self.dir_simu)
        else:
            self.dir_simu = dir_simu

        sbml_file = self.dir_simu + os.sep + os.path.basename(sbml_file)

        # Init conf file
        conf = self.dir_simu + os.sep + self.conf_file
        if not os.path.isfile(conf):
            self.init_conf()
            self.update_conf("graphs_dir", self.dir_graphs)
        else:
            self.load_conf()

        # Load sbml file
        ## Path to smbl file
        self.sbml_file = sbml_file
        ## Reference to sbml object
        self.sbml = SBML(sbml_file)
        self.is_sbml = True
        self.update_conf("sbml_file", os.path.basename(sbml_file))

    def init_conf(self):
        """
        Init simulation configuration (dict)
        """
        ## Simu configuration dict
        self.conf_dic = {
            "param_file" : "",
            "sbml_file" : "",
            "simu_dir" : {},
            "graph_file" : "",
            "graphs_dir" : "",
            "result" : False}

        self.write_conf()

    def update_conf(self, key, value):
        """
        Update configuration

        @param key
        @param value
        """
        self.conf_dic[key] = value
        self.write_conf()

    def write_conf(self):
        """
        Write configuration file
        """
        f = open(self.dir_simu + os.sep + self.conf_file, "w")
        json.dump(self.conf_dic, f, indent=4)
        f.close()

    def load_conf(self):
        """
        Load configuration file
        """
        f = open(self.dir_simu + os.sep + self.conf_file, "r")
        self.conf_dic = json.load(f)
        f.close()