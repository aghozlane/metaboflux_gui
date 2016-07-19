#!/usr/bin/python
# -*- coding: utf-8 -*-

from graph import *

import os, glob, re, csv, copy

class Result:
    """
    Result class manage metaboflux results.
    
    Look to directory results and search for histogram image
    Parse text file to allow graph generation with correct flux
    """
    
    def __init__(self, sbml, graph, dir_result, dir_log, dir_graphs, config, param):
        """
        Attributes initialisation

        @param sbml sbml object
        @param graph graph object (obsolete and useless)
        @param dir_result path to results directory to look for results file
        @param dir_log path to results directory to look for log file
        @param dir_graphs path to directory to generate new results graph
        @param config application configuration (dict)
        @param param Parameter file
        """

        # Results
        self.new_flux = [] # Filled by the self.get_get_graphs() method. Used in the gui/gtk/gresult.py module
        self.gp_final_amount = [] # Filled by the self.get_graphs() method. Used in the gui/gtk/gresult.py module
        self.histo = []           # Filled by the self.get_histo() method
        self.graphs = []          # Filled by the self.get_graphs() method
        self.log = []             # Filled by the self.get_log() method
        self.group_log = [] 
        self.sbml = sbml
        self.graph = graph
        self.dir_result = dir_result
        self.dir_log = dir_log
        self.dir_graphs = dir_graphs
        self.config = config
        self.param=param
        self.get_log()
        self.get_graphs()
        self.get_histo()
    
    def get_histo(self):
        """
        Look in results directory and search for histogram image using regexp
        """
        regexp = re.compile(".*.png")
        for f in glob.glob(self.dir_result + os.sep+ "*"):
            if regexp.match(os.path.basename(f)):
                self.histo.append(f)

    def get_graphs(self):
        """
        Look in results directory and search for mean_proportion file (using regexp).
        Parse file and extract solutions flux
        """
        minimization = self.config["resu_mini"]
        
        # Get group log file
        resu_file = None
        files=[".*_modeling_log.txt$",".*_group_log.txt$"]
        #files=[".*_group_log.txt$"]
        #files=[".*_log.txt$"]
        group=False
        #group=True
        for i in files:
            regexp = re.compile(i)
            #Get file 
            resu_file=self.get_result_file(regexp)
            self.get_flux_graph(resu_file,group)
            self.get_data_graph(resu_file,group)
            group=True
    
    def get_log_file(self,regexp):
        """
        Get the log filename
        @param regexp: Regex to find log files
        """
        regexp = re.compile(regexp)
        resu_file=None
        for f in glob.glob(self.dir_log + os.sep+"*"):
            if regexp.match(os.path.basename(f)):
                resu_file = f
                break
        return resu_file
    
    def get_log(self):
        """
        Get simulation log and convert it in list of list
        """
        # Get results file
        resu_file = None
        files=[".*_modeling_log.txt$",".*_group_log.txt$"]
        group=False
        for i in files:
            resu_file=self.get_log_file(i)
            # Parsing and looking for results in file
            if not resu_file:
                self.log = []
                self.group_log = []
                return 
            f = csv.reader(open(resu_file), delimiter='\t', quotechar='"')
            for l in f:
                if(group):
                    self.group_log.append(l)
                else:
                    self.log.append(l)
            group=True
     
    #Recuperation du fichier
    def get_result_file(self,regexp):
        """
        Load expected file
        @param regexp: Regex du fichier
        @return: Expected file
        """
        resu_file=None
        for f in glob.glob(self.dir_log + os.sep+"*"):
            if regexp.match(os.path.basename(f)):
                resu_file = f
                break
        return(resu_file)
    
    #Extraction des donnees du fichier group log
    def resu_head(self,nb_outputparameters, parameters,a):
      """
        Extraction of data from the group log file 
        @param parameters: Number of parameters
        @return: Reaction ratios of groups
      """
      sujet_etude =""
      if a:
          sujet_etude += "\S+\s+"
      sujet_etude += "\S+\s+"*(nb_outputparameters+1)
      sujet_etude += "(\S+)\s+"*parameters
      return sujet_etude
    
    #Energie ATP ADP NADH NAD Succ1 Succ2 Acetate parameters...
    def resu_data(self,nb_outputparameters, parameters,a):
      """
      Energy quantity parameters.
      @param nb_outputparameters: Number of Molecules
      @param parameters: Number of parameters for reaction ratios 
      """
      sujet_etude =""
      if a:
          sujet_etude +="(^H\d)\s+"
      sujet_etude += "[\-0-9]+.[0-9]+"
      #Molecules
      for i in range(nb_outputparameters):
        sujet_etude += ".[\-0-9]+"
      #Reaction ratios
      for i in range(parameters):
        sujet_etude += ".([\-0-9]+.[0-9]+)"
      return sujet_etude
        
    def get_flux_graph(self,resu_file,group):
        """
         Load flux data on graph
         @param resu_file: Data file
         @param group: Number of the group
        """
        tab=[]
        sol_energie=0
        resu_dic={}
        headregex =re.compile(self.resu_head(self.sbml.numSpecies,self.param.reaction,group))  
        regex = re.compile(self.resu_data(self.sbml.numSpecies,self.param.reaction,group))
        #Open result file  
        try:
            file_gp = open(resu_file, 'r')
            #Read result file
            for i in file_gp:
                a = regex.match(i)
                b = headregex.match(i)
                #If the regex match
                if a:
                    #recupere le groupe
                    subdic = {}
                    if(group):
                        #Recupere les ratio
                        for s in range(2,(2+self.param.reaction)):
                            subdic[tab[(s-2)]] = a.group(s)
                        #Sauvegarde le dico de tous les groupes
                        resu_dic[a.group(1)]=subdic
                    else:
                        sol_energie+=1
                        #Recupere les ratio
                        for s in range(1,(1+self.param.reaction)):
                            subdic[tab[(s-1)]] = a.group(s)
                            print(a.group(s))
                        #Sauvegarde le dico de toutes les energies
                        resu_dic[("B"+str(sol_energie))]=subdic
                    
                elif b:
                    #Recupere les noms des reactions
                    for j in range(1,(1+self.param.reaction)):
                        tab.append(b.group(j))
    
            self.new_flux.append(resu_dic)
            #Close file
            file_gp.close()
        except IOError:
            sys.stderr.write('The program cannot open %s'%resu_file)
            return
        except:
            sys.stderr.write('Something went wrong with %s'%resu_file)
            return        
        
    #Recuperation des donnees pour les graphes
    def get_data_graph(self,resu_file,group):
        """
         Load data on graph
         @param resu_file: Data file
        """
        if not resu_file:
            return
        else:
            resu_final_amount={}
            a=1
            sol_energie=0
            if(group):
                a=0
            file_gp = open(resu_file,'r')
            lines = file_gp.readlines()
            header1 = lines[0]
            header1 = header1.rstrip("\n")
            header1 = header1.rstrip("\t")
            
            header = header1.split("\t")
            for i in range (1,len(lines)):
                sol_energie+=1
                graph_h = {}
                line = lines[i].rstrip("\n")
                line = line.rstrip("\t")
                sline = line.split("\t")
                for j in range((1+a),len(sline)):
                    graph_h[header[j]] = sline[j]
                if group:
                    resu_final_amount[sline[0]] = graph_h
                else:                    
                    resu_final_amount[("B"+str(sol_energie))] = graph_h
        
        #Fermeture du fichier
        file_gp.close()         
        self.gp_final_amount.append(resu_final_amount) 