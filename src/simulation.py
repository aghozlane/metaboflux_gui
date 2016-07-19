#!/usr/bin/python
# -*- coding: utf-8 -*-

import shlex, subprocess, tempfile, os, shutil
import gobject

class Simulation:
    """
    Simulation class create a subprocess and launch metaboflux
    simulation giving in parameter a valid sbml file, a valid param
    file and all directory to receive results. Because the best way to
    launch a subprocess is putting it in a separated thread, ths class
    is very GUI specific.
    """
    
    def __init__(self, model, sbml_file, param_file,
                 dir_simu, config, result_dir=None):
        """
        Constructor : initalise all variable, ready to launch the simulation.

        @param model model object
        @param sbml_file path to sbml file
        @param param_file path to param file
        @param dir_simu directory of the current simulation (to receive results)
        @param config app configuration dictionary
        """

        # Simulation directory

        ## Subdirectory for simulation results
        self.result_dir_simu = config["resu_simu"]

        ## Subdirectory for statistic results
        self.result_dir_stat = config["resu_stat"]

        ## Subdirectory for minimisation results
        self.result_dir_mini = config["resu_mini"]

        ## Path to MetaBoFlux.py
        self.path_metabo = config["path_metabo"]

        ## Path to mpd daemon
        self.path_mpd = config["path_mpd"]

        # Set metaboflux parameters
        self.sbml_file = sbml_file
        self.param_file = param_file
        self.dir_simu = dir_simu

        if result_dir:
            self.result_dir_simu = str(result_dir["simu"])
            self.result_dir_stat = str(result_dir["stat"])
            self.result_dir_mini = str(result_dir["mini"])

        # Set model object
        self.model = model

        ## State of the simulation
        self.state = False

        ## Simulation is processing or not ?
        self.process = None

        ## Simulation has been stoped (STOP button pressed)
        self.stop = False

    def launch(self):
        pass

    def handle(self):
        pass
