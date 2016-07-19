#!/usr/bin/python
# -*- coding: utf-8 -*-

from simulation import *
from server_metabo import *
import shlex, subprocess, tempfile, os, shutil
import gobject, threading, gtk, thread
import re, glib, sys, signal, time

class GSimulation(Simulation, threading.Thread):
    """
    Simulation which launch a simulation (MetaBoFlux) subprocess
    """
    ugly=os.sep+".."+os.sep+".."+os.sep+".."+os.sep
    def __init__(self, model, sbml_file,
                 param_file, dir_simu,
                 config, result_dir = None):
        
        threading.Thread.__init__(self)
        Simulation.__init__(self, model, sbml_file,
                            param_file, dir_simu,
                            config, result_dir)
        self.pids = []
        
        self.file = os.path.join(os.path.dirname(__file__))+self.ugly+config['dir_tmp'] + config['progress']
        self.pid = os.path.join(os.path.dirname(__file__))+self.ugly+config['dir_tmp'] + 'pid.tmp'

    def launch(self, nb_core, regen = False):
        """
        Launch subprocess in separated thread of Interface
        """

        self.state = True
        d = self.dir_simu
        
        # Create directory structure
        if not os.path.isdir(d + self.result_dir_simu):
            os.makedirs(d + self.result_dir_simu)
        if not os.path.isdir(d + self.result_dir_stat):
            os.makedirs(d + self.result_dir_stat)
        if not os.path.isdir(d + self.result_dir_mini):
            os.makedirs(d + self.result_dir_mini)

        self.previous = ""

        # Launch server
        self.port = None
        self.good = False
        self.thread = thread.start_new_thread(self.launch_server,())

        # Wait for server init
        while True:
            if self.port and self.good:
                break
            gtk.main_iteration()

        # Launch glyco process and get stdout in tmp file
        self.log=""
        try:
            self.log = open(d+os.sep+"log_simu.txt", "w")
        #cmd = "python ../metaboflux/metaboflux.py " + d + self.result_dir_stat
        except IOError:
            self.model.disp_message("Error, Can not open file :%s"%self.log)
            return
        
        param_metabo = "-smr" + " -p " + str(self.port)
        if regen:
            param_metabo = "-r"
        #"python " +
        cmd = os.path.join(os.path.dirname(__file__))+self.ugly+self.path_metabo + "MetaBoFlux.py " + param_metabo
        if not nb_core == 0:
            cmd += " -t " + str(nb_core)
        cmd += " --par " + self.param_file + " --sbml " + self.sbml_file
        cmd += " --sim_out " + d + self.result_dir_simu
        cmd += " --min_out " + d + self.result_dir_mini
        cmd += " --stat_out " + d + self.result_dir_stat

        # Launch mpd
        #if not regen:
        #    try:
        #        self.mpd = subprocess.Popen(shlex.split(self.path_mpd),
        #                                    shell=False,
        #                                    stdout=subprocess.PIPE,
        #                                    stderr=subprocess.STDOUT)
        #    except:
        #        self.model.disp_message("Can't start mpd at : "
        #                                + self.path_mpd +
        #                                " - Maybe you need to configure metabo.conf file.")
        #        self.model.progress.destroy()
        #        self.state = False
        #        self.model.set_sensitive()
        #        return

        # Launch metaboflux
        try:
            self.process = subprocess.Popen(shlex.split(cmd),
                                            shell=False,
                                            stdout=self.log,
                                            stderr=subprocess.STDOUT)
        except:
            self.model.disp_message("Can not start program simulation (MetaBoFlux) at : "
                                    + self.path_mpd +
                                    " - Maybe you need to configure metabo.conf file.")
            self.model.progress.destroy()
            self.state = False
            self.model.set_sensitive()
            return

        gobject.timeout_add(200, self.handle, regen)

    def handle(self, regen):
        """
        Handle metaboflux process
        """
        if self.process.poll() == None and not self.stop:
            if os.path.isfile(self.file):
                fpg = open(self.file, "r")
                d = fpg.read()
                if d != self.previous and d.strip() != '':
                    self.manage_pulse(d.split("\n")[:-1])
                    self.previous = d
                fpg.close()
            return True
        
        elif self.stop and not regen:
            
            # Remove results directory
            self.remove_dir()
            # Get pid of subprocess
            pid = []
            f=""
            try:
                f = open(self.pid, "r")
                for l in f.readlines():
                    pid.append(l)
            except IOError:
                self.model.disp_message("Error, Can not open file :%s"%self.pid)
                return
                
            # Kill main subprocess
            os.kill(self.process.pid, signal.SIGKILL)
            
            # Kill other process
            for p in pid:
                try:
                    os.kill(int(p), signal.SIGKILL)
                except:
                    pass
            os.wait()

            # Kill mpd daemon
            #os.kill(self.mpd.pid, signal.SIGKILL)
        else:
            self.return_code = self.process.poll()
            self.state = False
            self.model.simu_is_done(self.dir_simu+self.result_dir_stat,
                                    self.dir_simu+self.result_dir_mini, regen)

        if os.path.isfile(self.file):
            os.remove(self.file)
        if os.path.isfile(self.pid):
            os.remove(self.pid)

        self.log.close()
        self.state = False
        gtk.gdk.threads_leave()
        return False

    def remove_dir(self):
        """
        Remove directory which contains results of the simulation
        """
        shutil.rmtree(self.dir_simu+self.result_dir_simu)
        shutil.rmtree(self.dir_simu+self.result_dir_mini)
        shutil.rmtree(self.dir_simu+self.result_dir_stat)

    def launch_server(self):
        """
        Init server which listen to metaboflux progression
        """
        self.port = 60003
        out = False
        while not out:
            try:
                self.server = SocketServer.ThreadingTCPServer(('', self.port), ServerMetabo)
            except socket.error:
                #print str(self.port) + " is already in use. Trying an other port ..."
                self.port += 1
            else:
                out = True
                
        self.good =True
        #print "Serveur is launch, waiting for connection on port " + str(self.port)
        self.server.serve_forever()

    def manage_pulse(self, pg):
        """
        Read pg and set progress bar according from progression
        """
        all_state = [ "Simulated annealing","Minimization", 
                     "Modeling", "Standard deviation estimation","Group analysis"]
        state = []
        reg_state = re.compile("^[a-zA-Z ]*$")
        reg_progress = re.compile("^\(\d{1}\/\d{1}\)$")
        for s in pg:
            if reg_state.match(s):
                state.append(s)

        try:
            index = None
            for i, s in enumerate(all_state):
                if s == state[-1:][0]:
                    index = i

            if reg_progress.match(str(pg[-1:][0])):
                n = int(pg[-1:][0][1])
            else:
                n = 0
            progress =  n + (index * 5)
            progress = float(progress) / float(24)

            self.model.progress.set_text(str(state[-1:][0]) + " "
                                         + str(int(progress*100)) + " %")
            self.model.progress.set_fraction(progress)
        except IndexError:
            return
