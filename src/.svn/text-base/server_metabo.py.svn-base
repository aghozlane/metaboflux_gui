#!/usr/bin/python
# -*- coding: utf-8 -*-

import SocketServer, socket, os, re, json, time

class ServerMetabo(SocketServer.BaseRequestHandler):
    """
    ServerMetabo class is a server which is created for each client
    made by MetaBoFlux.

    In normal situation, there is about 6-7 clients connecteds for one
    simulation. So 6-7 ServerMetabo instance will be created.
    Each instance write needed information by the GUI to a file and
    the GUI will read thsi informations to get the progress or
    processus pid for example.
    """

    def setup(self):
        """
        Overwrite setup method. This method is called when new client
        is connected.
        """
        # Config tmp file
        config=[]
        try:
            config_metabo=os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+"config.metabo"
            f = open(config_metabo, "r")
            config = json.load(f)
            f.close()
        except IOError:
            sys.exit("Error : file not found %s"%config_metabo)
        except:
            sys.exit("Something went wrong with config_metabo") 
        
        #print self.client_address[0], 'connected!'
        self.file = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+str(config["dir_tmp"]) + str(config["progress"])
        self.pid = os.path.join(os.path.dirname(__file__))+os.sep+".."+os.sep+str(config["dir_tmp"]) + str(config["pids"])
        self.ispid = re.compile("^\d*$")

    def handle(self):
        """
        Overwrite handle method. This method handles the client as the
        client closed the connection.
        """
        while True:
            self.data = self.request.recv(1024)
            if self.ispid.match(self.data):
                f = open(self.pid, "a")
                f.write(self.data + "\n")
                f.close()
            else:
                f = open(self.file, "a")
                f.write(self.data + "\n")
                f.close()
            if not self.data:
                break
        self.request.close()
