import threading
import logging
import os
import config
import cv2
from datetime import datetime

class FrameSaver(threading.Thread):

    def __init__(self, args=(), kwargs=None, index=None, name=None, addr=None):
        super().__init__()
        self.q = args
        self.kwargs = kwargs
        self.index = index

    def run(self):
        while True:
            qvalue = self.q.get()
            self.save_frame(qvalue)
            
    def save_frame(self, qvalue):
        cv2.imwrite(qvalue[0], qvalue[1])
        logging.debug("Saved Open CV camera image to: "+ str(qvalue[1]))
        