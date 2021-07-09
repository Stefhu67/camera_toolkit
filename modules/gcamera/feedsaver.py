import threading
import logging
import os, io
import config
from PIL import Image

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
        image = Image.open(io.BytesIO(qvalue[1]))
        image.load()
        image.save(qvalue[0])
        logging.debug("Saved gPhoto camera image to '%s'" % str(qvalue[0]))

        