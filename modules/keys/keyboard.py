import threading
import logging, sys
import config

class KeyMonitor(threading.Thread):

    def __init__(self, args=(), kwargs=None):
        super().__init__()
        self.q = args
        self.args = args
        logging.debug('Ready for keyboard input:')

    def run(self):
        while (True):
            input_str = input()
            self.q.put(input_str)

    def stop(self):
        sys.exit(1)
