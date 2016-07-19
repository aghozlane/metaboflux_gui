#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree
import re, shutil, os

class Param:
    """Management settings metaboflux in xml format"""

    # Declaration of attributs
    # Init with default values
    
    location = None
    xml = None
    
    first_parse_rep = True
    first_parse_math = True
    first_parse_species = True
    first_parse_values = True

    is_valid = None

    # Set default core numbers
    previous_nb_core = 0
    nb_core = 0
    
    def __init__(self, location, xml_file, sbml, config, open_simu=False):
        """Tree init with default values"""

        # Files
        self.schema_xml = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+config["path_schema_file"]
        self.param_xml = config["param_name"]

        # Parameters
        self.values = {}
        self.species = {}
        self.banned_compounds = []
        self.reactions_group = {}
        self.kinetic_law = {}
        self.representation = {}
        self.reaction=0

        # Etree object according to xml file
        self.xml = None
        self.root = None

        self.sbml = sbml
        self.xml_file = xml_file
        self.location = location + os.sep + self.param_xml
        
        if open_simu :
            self.param_xml = os.path.basename(self.xml_file)
        else:
            shutil.copy(xml_file, self.location)
            
        self.load(self.location)
                
    def valid(self, xml_to_valid=xml):
        """Valid a xml file with a schema file"""

        s = open(self.schema_xml, "r")

        # Parse and load validation schema
        xmlschema_doc = etree.parse(s)
        schema = etree.XMLSchema(xmlschema_doc)
        
        s.close()
        
        # Validation : return True of False
        return schema.validate(xml_to_valid)
    
    def write(self):

        if self.valid(self.xml):
            self.xml.write(self.location)
            return True
        else:
            print "Erreur d'ecriture du fichier xml non valide."
            return False

    def load(self, xml_file):

        # Open and parse xml file
        f=""
        try:
            f = open(xml_file, "r")
        except:
            return False

        self.xml = etree.parse(f)
                    
        self.is_valid = self.valid(self.xml)
        if self.is_valid:
                        
            # If file is valid, load root and all parameters in memory
            self.root = self.xml.getroot()

            # Load parameters
            self.get_values()
            self.get_species()
            self.get_banned_compounds()
            self.get_reactions_group()
            self.get_kinetic_law()
            self.get_representation()
            
            # Close sucessfully
            f.close()
            return True
        else:
            f.close()
            return False

    ###################################
    # Getters / Setters to param file #
    ###################################

    ######################
    # Handle with values #
    ######################
    def get_values(self):
        param = ["name", "nbSimulations", "nbtriesMod", "nbtriesSa", "nbiters",
                 "stepsize", "boltzmann", "Tinitial", "muT",
                 "Tmin", "groupSize", "nbGroup", "interestEnergy"]
        
        for c in self.root:
            if c.tag in param:
                self.values[c.tag] = c.text

        # Make a copy to allow a reset
        if self.first_parse_values:
            self.first_parse_values = False
            self.old_values = self.values.copy()
                
        return self.values

    def set_values(self, key, value):
        no_verif = ["name"]
        positive_numbers = ["nbSimulations",
                            "nbtriesMod",
                            "nbtriesSa",
                            "nbiters",
                            "stepsize",
                            "boltzmann",
                            "groupSize",
                            "nbGroup",
                            "interestEnergy",
                            "nb_core",
                            "Tinitial",
                            "muT",
                            "Tmin"]
        
        #negative_numbers = []
        
        integer_numbers = ["nbSimulations",
                           "nbtriesMod",
                           "nbtriesSa",
                           "nbiters",
                           "groupSize",
                           "nbGroup",
                           "interestEnergy",
                           "nb_core"]

        if value == "":
            return (False, "can't be empty")
        elif key in positive_numbers and \
                 not re.match("^[0-9]+[\.]?[0-9]*$", value):
            return (False, "must be positive number")
        #elif key in negative_numbers and \
        #         not re.match("^[-]?[0-9]+[\.]?[0-9]*$", value):
        #    return (False, "must be positive number")
        elif key in integer_numbers and \
                 not re.match("^[-]?[0-9]*$", value):
            return (False, "must be an integer")
        elif key == "nbtriesMod" and int(value) < 1:
            return (False, "nbtriesMod need to be >= 1")
        elif key == "nbtriesSa" and int(value) < 1:
            return (False, "nbtriesSa need to be >= 1")
        elif key == "nbiters" and int(value) < 1:
            return (False, "nbiters need to be >= 1")
        elif key == "stepsize" and float(value) < 1.0:
            return (False, "stepsize need to be >= 1.0")
        elif key == "nbSimulations" and int(value) < 3:
            return (False, "nbSimulations need to be > 3")
        elif key == "nbiters" and int(value) < 1:
            return (False, "nbiters need to be >= 1.0")
        elif key == "muT" and int(value) <= 1:
            return (False, "muT need to be >= 0.0")
        elif key == "boltzmann" and (float(value) < 1.0 or float(value) > 2.0):
            return (False, "nbiters need to be >=1.0 and <=2.0")
        elif key == "Tmin" and int(value) < 0.0:
            return (False, "Tmin need to be >= 0.0")
        elif key == "Tinitial" and float(value) < float(self.values["Tmin"]):
            return (False, "Tinitial need to be > Tmin")
        elif key == "nbGroup" and int(value) >= int(self.values["groupSize"]):
            return (False, "expected group need to be lower than considered simulations")
        elif key == "groupSize" and int(value) > int(self.values["nbSimulations"]):
            return (False, "considered simulations need to be lower than number of  simulations")
        elif key == "interestEnergy"  and int(value) > int(self.values["nbSimulations"]):
            return (False, "displayed energy need to be lower than number of  simulations")
        else:
            if key == "nb_core":
                self.previous_nb_core = self.nb_core
                self.nb_core = value
            else:
                self.values[key] = value
                element = self.root.find(key)
                element.text = value
            return (True, "")

    #######################
    # Handle with species #
    #######################

    def get_species(self):
        """
        Load finalAmount and ponderation from param file
        """
        for c in self.root:
            if c.tag == "listOfSpecies":
                for s in c:
                    self.species[s.attrib["id"]] = [s.attrib["finalAmount"], None]
                    if "weight" in s.attrib.keys():
                        self.species[s.attrib["id"]][1] = s.attrib["weight"]

        # Make a copy to allow a reset
        if self.first_parse_species:
            self.first_parse_species = False
            self.old_species = self.species.copy()
            
        return self.species

    def set_species(self, name, fAmount, weight="1", delete=False):

        # if name doesnt exist or amount different to 0
        # dictionnary of species amount is updated
        if ((name in self.species.keys() and fAmount != "0") or \
            (not name in self.species.keys() and fAmount != "0")) and not delete:
            if not name in self.species.keys():
                self.species[name] = [fAmount, weight]
            else:
                self.species[name][0] = fAmount
                self.species[name][1] = weight
        elif name in self.species and fAmount == "0" or delete:
            try:
                del self.species[name]
            except KeyError:
                return False
        else:
            return False

        # Synchronize self.root element according to self.species dico
        species_node = self.root.find("listOfSpecies")
        for s in species_node:
            # Remove all species nodes in listOfSpecies
            species_node.remove(s)

        for k, v in self.species.iteritems():
            new = etree.SubElement(species_node, "species")
            new.attrib["id"] = k
            new.attrib["finalAmount"] = v[0]
            new.attrib["weight"] = v[1]

        return True

    ################################
    # Handle with banned compounds #
    ################################

    def get_banned_compounds(self):
        for c in self.root:
            if c.tag == "listOfBannedCompounds":
                for s in c:
                    self.banned_compounds.append(s.attrib["id"])
        return self.banned_compounds

    def set_banned_compounds(self, name, delete=False):

        # if name doesnt exist or amount different to 0
        # dictionnary of species amount is updated
        if not name in self.banned_compounds and delete == False:
            self.banned_compounds.append(name)
        elif delete == True:
            self.banned_compounds.remove(name)
        else:
            return

        # Synchronize self.root element according to
        # self.banned_compounds dico
        banned_node = self.root.find("listOfBannedCompounds")
        for s in banned_node:
            # Remove all species nodes in listOfBannedCompounds
            banned_node.remove(s)

        for b in self.banned_compounds:
            new = etree.SubElement(banned_node, "compounds")
            new.attrib["id"] = b

        # Synchronize with sbml banned compounds
        self.sbml.list_banned = self.banned_compounds

    #########################
    # Handle with Reactions #
    #########################
    
    #### > is ok (13/09/2010)
    # Load the settings parameters from the XML file,if the len(self.reactions_group)=0
    # Else, it only returns the self.reactions_group hash
    def get_reactions_group(self):
        """
        Get information on reaction in the xml
        @return: self.reactions_group hash
        """
        self.reactions_group={}
        self.reaction=0
        c = self.root.find("listOfReactions")
        for s in c:
            #decompte du nombre de raction
            self.reaction+=len(s)
            l = []
            #Recuperation des reactions
            for r in s:
                l.append(r.attrib['id'])
                self.reactions_group[s.attrib["reference"]] = l

        return self.reactions_group
    
    def set_reactions_group(self, reference, reactions_list, delete=False):
        if not reference in self.reactions_group.keys() and \
               len(reactions_list) != 0:
            self.reactions_group[reference] = reactions_list
        elif delete:
            del self.reactions_group[reference]
        else:
            return False

        ## Synchronize self.root element according to self.reactions_group dico ##

        # Get the listOfReactions node object
        reactions_group_node = self.root.find("listOfReactions")
        reactions_group_node.clear()
        
        n_id=0;
        for r, l in self.reactions_group.iteritems():
            new = etree.SubElement(reactions_group_node, "noeud")
            new.attrib["reference"] = str(n_id)
            n_id += 1
            for reac in l:
                new_reac = etree.SubElement(new, "reaction")
                new_reac.attrib["id"] = reac


    ###########################
    # Handle with kinetic law #
    ###########################

    def get_kinetic_law(self):
        for c in self.root:
            if c.tag == "listOfKineticlaw":
                for math in c:
                    l = []
                    for ele in math[0]:
                        l.append(ele.text)
                    self.kinetic_law[math.attrib["display"]] = l

        # Make a copy to allow a reset
        if self.first_parse_math:
            self.first_parse_math = False
            self.old_kinetic_law = self.kinetic_law.copy()
                    
        return self.kinetic_law

    def set_kinetic_law(self, equation="", math=None, delete=False):
        code = None
        
        if not math:
            math = "block_" + str((len(self.kinetic_law)))

        if len(equation) != 0 and not delete:
            self.kinetic_law[math] = equation
        elif delete:
            if equation not in self.kinetic_law.keys():
                code = False
            del self.kinetic_law[math]
            code = True
        else:
            code = False

        # Synchronize self.root element according to self.reactions_group dico
        kinetic_law_node = self.root.find("listOfKineticlaw")
        for s in kinetic_law_node:
            # Remove all species nodes in listOfSpecies
            kinetic_law_node.remove(s)

        for m, equ in self.kinetic_law.iteritems():
            new = etree.SubElement(kinetic_law_node, "math")
            new.attrib["display"] = m
            
            new_mrow = etree.SubElement(new, "mrow")

            regexp = re.compile("[0-9]*")
            for ele in equ:
                if ele in ["+", "-", "/", "*", "=", ">", "<", ">=", "<="]:
                    ward_name = "mo"
                elif regexp.match(ele).group():
                    ward_name = "mn"
                else:
                    ward_name = "mi"
                new_ele = etree.SubElement(new_mrow, ward_name)
                new_ele.text = ele

        if code:
            return code
        else:
            return (True, math)

    ##############################
    # Handle with representation #
    ##############################

    def get_representation(self):
        for c in self.root:
            if c.tag == "representations":
                for g in c:
                    if g.tag == "graph":
                        self.representation[g.attrib["reference"]] = \
                        {"title" : g.attrib["title"],
                         "subtitle" : g.attrib["subtitle"],
                         "xtext" : g.attrib["xtext"],
                         "ytext" : g.attrib["ytext"],
                         "height" : g.attrib["height"],
                         "width" : g.attrib["width"]}
                        
        # Make a copy to allow a reset
        if self.first_parse_rep:
            self.first_parse_rep = False
            self.old_representation = self.representation.copy()
        return self.representation

    def set_representation(self, ref, value_type, value, debug=False):

        ref = str(int(ref))

        # if reference don't exist
        # it's impossible to create a new one
        if not ref in self.representation.keys():
            print "Error, the reference don't exist"
            return False
        #if the reference is already existing
        #the dictionnary is updated
        else:
            self.representation[ref][value_type] = value

            # Synchronize self.root element according to
            # self.representation dictionnary
            representation_node = self.root.find("representations")
            for r in representation_node:
                # Remove all graph nodes in representations
                representation_node.remove(r)

            #add new attributs to update 
            for k, v in self.representation.iteritems():
                new = etree.SubElement(representation_node, "graph")
                new.attrib["reference"] = k
                    
                l = ["title", "subtitle", "xtext", "ytext", "height", "width"]
                for i in l:
                    new.attrib[i] = self.treat_string(v[i])
            return True

    def treat_string(self, string):
        """
        Post treatment of string to replace value like %ns, %eg, %ce
        by correct value
        """

        corresp = {'ns' : self.get_values()["nbSimulations"],
                   'eg' : self.get_values()["nbGroup"],
                   'ce' : self.get_values()["groupSize"]}

        for r in re.findall("%([a-z]{2})", string):
            string = string.replace('%' + r, corresp[r])

        return string
