#!/usr/bin/python
# -*- coding: utf-8 -*-


from sbml import *
from gvgen import *

import shlex, subprocess, tempfile, glob
import time, gtk, threading, sys

class Graph(threading.Thread):
    """
    Graph class create graph image file according from the network described in sbml object.
    It launch a separated thread to launch dot program
    """

    isDone = threading.Event()
    
    def __init__(self, sbml, path, config, graph_file=None):
        """
        Initialization of class attribute and launch method to fin
        'dot' program on the OS

        @param sbml sbml object
        @param path path of the simulation
        @param config application configuration (dict)
        @param graph_file image name of the generated graph
        """
        threading.Thread.__init__(self)
        
        ## Configuration dictionnary
        self.config = config

        ## Image name of the generated graph
        self.image_name = self.config["graph_name"]

        ## Path to the dot program
        self.dot = self.config["graphviz_binary"]

        ## Image format
        self.format = self.config["file_format"]

        ## SBML object
        self.sbml = sbml

        ## Path where to put graph
        self.path_to_render = path + os.sep
        if graph_file:
            self.image_name = graph_file

        ## Graph object
        self.graph = None

        ## Flag to know of graph generation is done or not
        self.generate = False

        ## Final Amount to display on graph
        self.finalAmount = {}

        ## Nodes reaction to display on graph
        self.nodes_reac = {}

        ## Flux to display on graph
        self.flux = {}

        ## Reference to the subprocess
        self.proc = None

        # Find graphviz binary
        self.dot = self.find_graphviz()
        if not self.dot['dot']:
            print "Graphviz is not installed."
            print "Please install it before to use MetaBoflux GUI"
            sys.exit(1)
        
    def stop(self):
        """
        Stop signal to the thread
        """
        self.isDone.set()

    def get_graph(self):
        """
        Return full path to the generated image
        """
        return self.path_to_render + self.image_name

    def get_label(self, species):
        """
        Return html string specific to a species reference: species, initial amount (sbml), final amount.

        @param species species wich will be labelised in HTML
        """
        
        sbmlFinalAmount = self.sbml.get_final_amount(species)
        # self.finalAmount is filled by the get_finalamount method, in the result.py module
        if self.sbml.get_name(species) in self.finalAmount.keys(): 
            sbmlFinalAmount = self.finalAmount[self.sbml.get_name(species)] 
        
        if type(sbmlFinalAmount).__name__ == 'list':
            sbmlFinalAmount = int(sbmlFinalAmount[0])

        return """<<table border=\"0\" align=\"center\">
        <tr>
        <td colspan=\"2\">%s</td>
        </tr>
        <tr>
        <td><font color=\"blue\">%i</font></td>
        <td><font color=\"red\">%i</font></td>
        </tr>
        </table>>""" \
    % (self.sbml.get_name(species),
       self.sbml.get_initial_amount(species),
       int(sbmlFinalAmount))

    def render(self, name=None):
        """
        Generate render of graph

        @param name name of the image file
        """

        if not name:
            name = self.image_name
        
        gv_file = tempfile.NamedTemporaryFile(delete=False)
        ## Full path to image file
        self.img_path = self.path_to_render + name

        # We try to remove last graph image before generation
        try:
            os.remove(self.img_path)
        except OSError:
            pass

        dot = self.graph.dot(gv_file)
        cmd = self.dot['dot'] + " -T" + self.format + " " + \
              gv_file.name + " -o" + self.img_path

        gv_file.close()

        if self.proc and self.proc.poll() == None:
            self.proc.kill()

        self.proc = subprocess.Popen(shlex.split(cmd),
                                     shell=False,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        
    def set_flux(self, species, reaction, flux, link):
        """
        Add custom flux on the graph object

        @param species focused
        @param reaction focused
        @param flux list of flux
        @param link where to display the flux
        """
        
        reac_name = self.sbml.get_name(reaction)
        nflux = 100
        if species in flux.keys() and reac_name in flux[species].keys():
            self.graph.propertyAppend(link,
                                      "label",
                                      (str(flux[species][reac_name]) + " %"))
            self.graph.propertyAppend(link, "fontcolor", "red")
            self.graph.propertyAppend(link, "color", "red")
            nflux = int(float(flux[species][reac_name]))
            
        elif self.sbml.get_flux(reaction):
            self.graph.propertyAppend(link, "label", (str(self.sbml.get_flux(reaction)) + " %"))
            nflux = self.sbml.get_flux(reaction)

        thickness = 1
        if not nflux == 100 and nflux > 10:
            thickness = nflux / 10
        self.graph.propertyAppend(link, "penwidth", thickness)

    def set_nodes_reac(self, reac, node):
        """
        Set special property to selectionned node

        @param reac reaction focused
        @param node nodes focused
        """
        list_reac = []
        for k, v in self.nodes_reac.iteritems():
            list_reac += v
        if self.sbml.get_name(reac) in list_reac:
            self.graph.propertyAppend(node, "fontcolor", "black")
            self.graph.propertyAppend(node, "fillcolor", "pink")
            self.graph.propertyAppend(node, "shape", "box")
            self.graph.propertyAppend(node, "style", "solid, rounded,filled")
        
    def gen_graph(self, flux={}, nodes_reac={}, finalAmount={}):
        """
        Algorithm to graph object creation (with gvgen).

        @param list of flux to display
        @param nodes_reac list of nodes to display
        @param finalAmount list of finalAmount to display
        """

        self.generate = False
        self.nodes_reac = nodes_reac
        self.flux = flux
        if finalAmount:
            self.finalAmount = finalAmount

        # Graph initialisation
        self.graph = GvGen()
        self.graph.smart_mode = 1

        # Style creation
        # Reac style
        self.graph.styleAppend("Reac", "style", "rounded,filled")
        self.graph.styleAppend("Reac", "fillcolor", "lightblue")
        self.graph.styleAppend("Reac", "shape", "rectangle")

        # Species style
        self.graph.styleAppend("Species", "color", "blue")

        # Banned style
        self.graph.styleAppend("Banned", "fontsize", "11")
        self.graph.styleAppend("Banned", "color", "darkgreen")
        self.graph.styleAppend("Banned", "fontcolor", "darkgreen")
        self.graph.styleAppend("Banned", "fixedsize", "true")
        self.graph.styleAppend("Banned", "height", "0.4")

        # Compartments creation
        compartments_nodes = {}
        for i in self.sbml.compartments:
            name = self.sbml.get_name(i)
            compartments_nodes[name] = self.graph.newItem(name)

        # List of graph nodes to avoid node duplication
        nodes = {}

        # Iteration on reactions / products and reactants
        # Add each node to graph
        for r in self.sbml.reactions:

            comp = self.sbml.get_compartment(r)
            if comp == None:
                node = self.graph.newItem(self.sbml.get_name(r))
            else:
                node = self.graph.newItem(self.sbml.get_name(r),
                                          compartments_nodes[comp])
                
            self.graph.styleApply("Reac", node)
            
            # If reac is in selectionned nodes
            # We put it highlighted
            self.set_nodes_reac(r, node)

            for a in self.sbml.get_reactants(r):
                flag = True
                species_name = self.sbml.get_name(a)

                if not species_name in nodes.keys():
                    node_a = self.graph.newItem(species_name,
                                                compartments_nodes[self.sbml.get_compartment(a)])

                    # Apply style
                    self.graph.propertyAppend(node_a, "label", self.get_label(a))
                    self.graph.styleApply("Species", node_a)

                    # Add node to nodes list
                    nodes[species_name] = node_a
                else:
                    node_a = nodes[species_name]

                # Link creation, and reverse link creation if reaction
                # is reversible
                link = self.graph.newLink(node_a, node)
                self.set_flux(species_name, r, flux, link)
                if self.sbml.is_reversible(r):
                    self.graph.newLink(node, node_a)

            for p in self.sbml.get_products(r):
                species_name = self.sbml.get_name(p)

                if not species_name in nodes.keys():
                    node_p = self.graph.newItem(\
                        species_name, compartments_nodes[self.sbml.get_compartment(p)])

                    # Apply style
                    self.graph.propertyAppend(node_p, "label", self.get_label(p))
                    self.graph.styleApply("Species", node_p)

                    # Add node to nodes list
                    nodes[species_name] = node_p
                else:
                    node_p = nodes[species_name]

                # Link creation, and reverse link creation if reaction
                # is reversible
                self.graph.newLink(node, node_p)
                if self.sbml.is_reversible(r):
                    self.graph.newLink(node_p, node)

            for t, b in self.sbml.get_banned(r).iteritems():
                for s in b:
                    species_name = self.sbml.get_name(s)
                    comp = self.sbml.get_compartment(r)
                    if comp == None:
                        node_s = self.graph.newItem(species_name)
                    else:
                        node_s = self.graph.newItem(species_name,
                                                    compartments_nodes[comp])

                    self.graph.styleApply("Banned", node_s)

                    if t == "reactants":
                        self.graph.newLink(node_s, node)
                    else:
                        self.graph.newLink(node, node_s)


    ###################################################################
    # The multi-platform version of this 'find_graphviz' function was #
    # contributed by Peter Cock found :                               #
    # http://code.google.com/p/pydot/source/browse/trunk/pydot.py     #
    ###################################################################
    def find_graphviz(self):
        """
        Locate Graphviz's executables in the system.

        Tries three methods:

        First: Windows Registry (Windows only)
        This requires Mark Hammond's pywin32 is installed.

        Secondly: Search the path
        It will look for 'dot', 'twopi' and 'neato' in all the directories
        specified in the PATH environment variable.

        Thirdly: Default install location (Windows only)
        It will look for 'dot', 'twopi' and 'neato' in the default install
        location under the 'Program Files' directory.

        It will return a dictionary containing the program names as keys
        and their paths as values.

        If this fails, it returns None.
        """

        # Method 1 (Windows only)
        #
        if os.sys.platform == 'win32':

            try:
                import win32api, win32con

                # Get the GraphViz install path from the registry
                #
                hkey = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\ATT\Graphviz", 0, win32con.KEY_QUERY_VALUE)

                path = win32api.RegQueryValueEx(hkey, "InstallPath")[0]
                win32api.RegCloseKey(hkey)

                # Now append the "bin" subdirectory:
                #
                path = os.path.join(path, "bin")
                progs = self.__find_executables(path)
                if progs is not None :
                    #print "Used Windows registry"
                    return progs

            except ImportError :
                # Print a messaged suggesting they install these?
                pass


        # Method 2 (Linux, Windows etc)
        if os.environ.has_key('PATH'):

            for path in os.environ['PATH'].split(os.pathsep):
                progs = self.__find_executables(path)
                if progs is not None :
                    #print "Used path"
                    return progs

        # Method 3 (Windows only)
        #
        if os.sys.platform == 'win32':

            # Try and work out the equivalent of "C:\Program Files" on this
            # machine (might be on drive D:, or in a different language)
            #

            if os.environ.has_key('PROGRAMFILES'):

                # Note, we could also use the win32api to get this
                # information, but win32api may not be installed.

                path = os.path.join(os.environ['PROGRAMFILES'], 'ATT', 'GraphViz', 'bin')

            else:

                #Just in case, try the default...
                path = r"C:\Program Files\att\Graphviz\bin"

            progs = self.__find_executables(path)

            if progs is not None :

                #print "Used default install location"
                return progs


        for path in (
            '/usr/bin', '/usr/local/bin',
            '/opt/bin', '/sw/bin', '/usr/share',
            '/Applications/Graphviz.app/Contents/MacOS/'):

            progs = self.__find_executables(path)
            if progs is not None :
                #print "Used path"
                return progs

        # Failed to find GraphViz
        #
        return None

    def __find_executables(self, path):
        """Used by find_graphviz

        path - single directory as a string

        If any of the executables are found, it will return a dictionary
        containing the program names as keys and their paths as values.

        Otherwise returns None
        """

        success = False
        progs = {'dot': '', 'twopi': '', 'neato': '', 'circo': '', 'fdp': ''}

        was_quoted = False
        path = path.strip()
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
            was_quoted = True

        if os.path.isdir(path) : 
            for prg in progs.keys():
                if progs[prg]:
                    continue
                if os.path.exists(os.path.join(path, prg)):
                    if was_quoted:
                        progs[prg] = '"' + os.path.join(path, prg) + '"'
                    else:
                        progs[prg] = os.path.join(path, prg)
                    success = True
                elif os.path.exists(os.path.join(path, prg + '.exe')):
                    if was_quoted:
                        progs[prg] = '"' + os.path.join(path, prg + '.exe') + '"'
                    else:
                        progs[prg] = os.path.join(path, prg + '.exe')
                    success = True
        if success:
            return progs
        else:
            return None
