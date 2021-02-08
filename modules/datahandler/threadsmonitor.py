import threading, os, glob
from os import path
import logging, sys
import config
import time
import queue
import cv2
import shutil
from .dbmanager import Entry


class Clipboard(threading.Thread):

    def __init__(self, args=(), kwargs=None):
        super().__init__()
        self.queues = args
        self.kwargs = kwargs
        self.dbqueue = queue.Queue(maxsize=0)
        self.dbthread = Entry(args = (self.dbqueue))
        shutil.copy(config.data_export_script, config.experiment_path+"data_export.py")
        if not os.path.exists(config.experiment_path+config.status+"/"):
            os.makedirs(config.experiment_path+config.status+"/")

    def run(self):
        self.dbthread.start()
        last_grab = time.time() - 99999
        while True:
            if config.run == False:
                break
            if time.time() - last_grab > config.timestep and all(value == True for value in config.devices.values()):
                config.trigger = True
                logging.debug("TIME FOR A SHOT " + str(time.time() - last_grab ))
                last_grab = time.time()
                logging.debug("config.trigger is TRUE")
                logging.debug("The queue contains "+str(len(self.queues.items())) + " objects.")
                cycle_results = {}
                for device, q in self.queues.items():
                    try:
                        qvalue = q.get()
                        cycle_results[device] = qvalue
                    except queue.Empty:
                        pass
                logging.debug(cycle_results)
                self.dbqueue.put(cycle_results)
                config.trigger = False
                config.count += 1
                logging.debug("config.trigger is FALSE")
                logging.warning("Count "+ str(config.count))

    def stop(self):
        sys.exit(1)