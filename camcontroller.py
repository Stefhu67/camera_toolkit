import config
import queue
import time
import logging
from modules import *

logger = logging.getLogger('camcontroller')
logging.basicConfig(level=logging.WARNING,
                    format='(%(threadName)-9s) %(message)s',)
fh = logging.FileHandler('camcontroller.log')
fh.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.WARNING)
logger.addHandler(fh)
logger.addHandler(consoleHandler)

config.run = True
logging.warning("Config.run is True")


if config.serial == False:
    config.continuous_serial = False

buffers = {}
threads = {}
i = 0

if config.DSLR:
        setup_DSLRs = GPhotoUtils()
        for gcamera in setup_DSLRs.camera_list:
            name = gcamera[0]
            addr = gcamera[1]
            buffers["gcamera"+str(i)] = queue.Queue(maxsize=1)
            if config.DSLR_continuous == False:
                threads["gcamera"+str(i)] = GPhotoCamera(args =(buffers["gcamera"+str(i)]), index=i, name=gcamera[0], addr=gcamera[1]) 
            else:
                threads["gcamera"+str(i)] = GPhotoFeed(args =(buffers["gcamera"+str(i)]), index=i, name=gcamera[0], addr=gcamera[1]) 
            i += 1


if config.opencv:
    opencv_cameras = CV2Utils.returnCameraIndexes()
    opencv_best_res = CV2Utils.returnCameraResolutions( opencv_cameras )
    for cvcamera in opencv_cameras:
        buffers["ocamera"+str(cvcamera)] = queue.Queue(maxsize=1)
        threads["ocamera"+str(cvcamera)] = WebcamVideoStream( q = buffers["ocamera"+str(cvcamera)], src = int(cvcamera), width = opencv_best_res[0], height = opencv_best_res[1])

if config.serial:
    serial_buffer = queue.Queue(maxsize=1)
    arduino = DAQReader(args = (serial_buffer), baudrate = config.serial_baudrate ,port = config.serial_port)
    buffers["arduino"] = serial_buffer
    threads["arduino"] = arduino

clips = Clipboard(args =(buffers))
threads["clips"] = clips
inputQueue = queue.Queue()
keyboard = KeyMonitor( args=(inputQueue) )

for key, thread in threads.items():
    logging.debug("Starting thread: " + key)
    thread.start()
if config.continuous_serial == True:
    continuous_logger = DAQLogger(args = (serial_buffer))
    continuous_logger.start()


keyboard.start()
logging.warning("Press 'Q' to exit.")
while (True):
    if (inputQueue.qsize() > 0):
        input_str = inputQueue.get()
        logging.debug("input_str = {}".format(input_str))
        if (input_str == "q"):
            config.run = False
            logging.debug("Exiting serial terminal.")
            logging.warning("Wait for the connection closed signal before Ctrl+C...")
            break 

config.run = False  
logging.debug("Config.run is False")
time.sleep(3)

for key, thread in threads.items():
    thread.join()

sys.exit(1)