#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, shutil
from libsbml import *

class SBML:
    """
    SBML class offers a high level abstraction with sbml file. It can
    open and load sbml file. It checks if it's valid sbml file and can
    generate errors log file if not.
    There is various getter method which allow to read data from sbml file.
    There is not input method to sbml file.

    libSBML is used to read sbml file.
    """
    
    def __init__(self, xml):
        """
        Constructor : load file, initalise data (ready to read) if
        this is a velid sbml file and generate errors lof file if not.

        @param xml path to sbml file
        """

        ## Path to sbml file
        self.sbml_file = xml

        ## Valid sbml file is loaded
        self.is_load = False
        
        ## Container for an SBML document and interface for global
        ## operations on SBML documents. (libsbml object)
        self.doc = readSBML(self.sbml_file)

        # Valid SBML file
        self.valid()

        if self.valid:
            self.init()

    def init(self):
        """
        SBML data initialisation. Read all basic data from sbml
        file. Further data access will be very quick. Set is_load to
        True if initalisation wroked.
        """

        ## Model object of sbml file (libsbml object)
        self.model = self.doc.getModel()

        ## All species in sbml (libsbml object)
        self.species = self.model.getListOfSpecies()

        ## All reactions in sbml (libsbml object)
        self.reactions = self.model.getListOfReactions()

        ## All compartments in sbml (libsbml object)
        self.compartments = self.model.getListOfCompartments()
        
        #Number of species
        self.numSpecies = self.model.getNumSpecies()

        ## List of hypotetic banned compounds based on their name
        ## (*ATP*, *ADP*, etc)
        self.list_banned = []
        self.get_hypotetic_compounds_list()

        self.is_load = True

    def valid(self):
        """
        Log generation when new sbml file is loaded. Set valid to True
        if sbml file passed the validation process.
        """
        ## Sbml file validation state
        self.valid = True
        log = ""

        for i in range(self.doc.checkConsistency()):
            e = self.doc.getError(i)
            log += str("line " + str(e.getLine()) + " -> ",)
            log += str(e.getSeverityAsString() + " : ",)
            log += str(e.getMessage())

            # Check if valid
            if e.getSeverityAsString() in ["Error", "Fatal"]:
                self.valid = False
        
        for i in range(self.doc.checkInternalConsistency()):
            e = self.doc.getError(i)
            log += str("line " + str(e.getLine()) + " -> ",)
            log += str(e.getSeverityAsString() + " : ",)
            log += str(e.getMessage())

            # Check if valid
            if e.getSeverityAsString() in ["Error", "Fatal"]:
                self.valid = False

        ## Warning, erros and fatal message to sbml file
        self.errors_message = log
        
    def set_banned_compounds(self, species_name):
        """
        Add banned compounds to list.

        @param species_name name of banned compounds
        @return True if species_name not already in list
        """
        if species_name not in self.list_banned:
            self.list_banned.append(species_name)
            return True
        else:
            return False

    def get_hypotetic_compounds_list(self):
        """
        Look for hypotetic banned compounds in sbml species.
        Research is based on the next regexp : '.*N*A[TD][HP].*'
        """
        regexp = re.compile(".*N*A[TD][HP].*")
        for i in self.species:
            if regexp.match(i.getId().upper()):
                self.list_banned.append(i.getId())

    def get_banned(self, reactions):
        """
        Return dict of lists of banned compounds as species
        reference object for all reactions

        @param reactions reactions object (libsbml object)
        @return banned_list banned compounds dict
        """
        banned_list = { 'reactants' : [] , 'products' : [] }
        for a in reactions.getListOfReactants():
            if self.is_banned(a):
                banned_list['reactants'].append(a)
        for p in reactions.getListOfProducts():
            if self.is_banned(p):
                banned_list["products"].append(p)
        return banned_list
                
    def is_banned(self, species_ref):
        """
        Search if species reference is a banned component or not.

        @param species_ref reference to species
        """
        name = species_ref.getSpecies()
        if name in self.list_banned:
            return True
        return False
    
    def get_name(self, obj):
        """
        Name of the object in consideration.

        @param obj libsbml object (Reference, Species, Reactions)
        @return name's object
        """
        if str(obj.__class__).find("Reference") != -1:
            return obj.getSpecies()
        else:
            return obj.getId()

    def get_species(self, ref):
        """
        Return Species object of one SpeciesReference

        @param ref species reference
        @return species or False if ref does not exist
        """
        for i in self.species:
            if i.getId() == ref.getSpecies():
                return i
        return False

    def get_object(self, name):
        """
        Return object according to his name.

        @param name name (string)
        @return libsbml object or False if name does not exist.
        """
        for r in self.reactions:
            if r.getId() == name:
                return r
        for i in self.species:
            if i.getId() == name:
                return i
        return False
        
    def is_reversible(self, reaction):
        """
        Test if reaction is reversible or not.

        @param reaction reaction libsbml object
        @return True is reaction is reversible
        """
        return reaction.getReversible()
        
    def get_reactants(self, reaction, banned=False):
        """
        Return list of reactants as species reference object except
        banned compounds.

        @param reaction reaction libsbml object
        @param banned allow banned compounds in reactants or not
        @return reac_list list of reactants (species reference libsbml object)
        """
        reac_list = []
        for a in reaction.getListOfReactants():
            if not self.is_banned(a) or banned:
                reac_list.append(a)
        return reac_list

    def get_products(self, reaction):
        """
        Return list of poducts as species reference object except
        banned compounds.

        @param reaction reaction libsbml object
        @return reac_list list of products (species reference libsbml object)
        """
        reac_list = []
        for p in reaction.getListOfProducts():
            if not self.is_banned(p):
                reac_list.append(p)
        return reac_list

    def get_compartment(self, obj):
        """
        Compartment of Reactions or SpeciesReference

        @param obj libsbml object (Reference or Reaction)
        @return compartment name
        """
        if str(obj.__class__).find("Reference") != -1:
            for i in self.species:
                if i.getId() == self.get_name(obj):
                    return i.getCompartment()
                
        elif str(obj.__class__).find("Reaction") != -1:
            for i in obj.getListOfReactants():
                if not i.getSpecies() in self.list_banned:
                    return self.get_species(i).getCompartment()
        else:
            return False

    def get_initial_amount(self, obj):
        """
        Initial amount of specified species

        @param obj name or reference object to the species
        @return initial amount (integer)
        """
        if str(obj.__class__).find("str") != -1:
            s = self.get_object(obj)
            return s.getInitialAmount()
                
        elif str(obj.__class__).find("Reference") != -1:
            return self.get_species(obj).getInitialAmount()

    def get_final_amount(self, species):
        """
        Final amount of specified species
        
        @param obj name or reference object to the species
        @return initial amount (integer)
        """
        return 0

    def get_flux(self, reaction):
        """
        Flux of reaction

        @param reaction reaction libsbml object
        @return flux (integer)
        """
        return reaction.getKineticLaw().getMath().getInteger()

    def get_nodes(self, group):
        """
        Possible nodes.

        @param group
        @return dict of nodes
        """
        # Get dico : {"reactants":[list of reaction]}
        dico = {}
        for r in self.reactions:
            for ra in self.get_reactants(r):
                if not dico.has_key(self.get_name(ra)):
                    dico[self.get_name(ra)] = []
                dico[self.get_name(ra)].append(self.get_name(r))
                
        nodes_dico = {}
        i = 0
        for k, v in dico.iteritems():
            if len(v) > 1 and not self.is_in_list(group, v):
                while str(i) in group.keys():
                    i += 1
                nodes_dico[str(i)] = v
                i += 1

        for k, v in group.iteritems():
            nodes_dico[k] = v
            
        return nodes_dico

    def is_in_list(self, list, sublist):
        """
        Check if sublist is included in list

        @param list parent list
        @param sublist sublist
        @return True if sublist is included in list
        """
        for k, v in list.iteritems():
            for i in v:
                for s in sublist:
                    if i == s:
                        return True
        return False

    def get_clean_flux(self, dic):
        """
        Convert libsbml object reaction dict in dict of dict with
        reactants as key.

        @param dic reaction libsbml object dict
        @return clean_dic converted dict
        """
        clean_dic = {}
        for k, v in dic.iteritems():
            reac = self.get_reactants(self.get_object(k), banned=False)
            if reac:
                reac_name = self.get_name(reac[0])
                if not reac_name in clean_dic.keys():
                    clean_dic[reac_name] = {}
                clean_dic[reac_name][k] = v
        return clean_dic
