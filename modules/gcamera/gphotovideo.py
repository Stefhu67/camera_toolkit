import gphoto2 as gp
import logging, time, os, sys, io
import config
import threading
import queue
from .feedsaver import FrameSaver

class GPhotoFeed(threading.Thread):

    def __init__(self, args=(), kwargs=None, index=None, name=None, addr=None):
        super().__init__()
        self.q = args
        self.kwargs = kwargs
        self.index = index
        self.name = name
        if not os.path.exists(config.experiment_path+config.status+"/"):
            os.makedirs(config.experiment_path+config.status+"/")
        self.init_gcam(index, name, addr)
        self.start_capture_view()
        self.save_frame_q = queue.Queue(maxsize=1)
        self.fsaver = FrameSaver( args = (self.save_frame_q),  )
        self.fsaver.start()
        config.devices[self.name+str(self.index)] = True

    def init_gcam(self, index, name, addr):
        self.camera = gp.Camera()
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        idx = port_info_list.lookup_path(addr)
        self.camera.set_port_info(port_info_list[idx])
        try:
            self.camera.init() # prints: WARNING: gphoto2: (b'gp_context_error') b'Could not detect any camera' if logging set up
            self.hasCamInited = True
        except Exception as ex:
            self.hasCamInited = False
            lastException = ex
            logging.warning("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))

    def start_capture_view(self):
        if self.hasCamInited:
            camera_config = self.camera.get_config()
            camera_model = self.get_camera_model(camera_config)
            self.put_camera_capture_preview_mirror(self.camera, camera_config, camera_model)
            logging.debug("Started capture view (extended lens/raised mirror) on camera: {}".format(camera_model))
        else: # camera not inited
            logging.debug("Sorry, no camera present, cannot execute command; exiting.")
            sys.exit(1)

    def event_text(self, event_type):
        if event_type == gp.GP_EVENT_CAPTURE_COMPLETE: return "Capture Complete"
        elif event_type == gp.GP_EVENT_FILE_ADDED: return "File Added"
        elif event_type == gp.GP_EVENT_FOLDER_ADDED: return "Folder Added"
        elif event_type == gp.GP_EVENT_TIMEOUT: return "Timeout"
        else: return "Unknown Event"

    def empty_queue(self):
        typ,data = self.camera.wait_for_event(200)
        while typ != gp.GP_EVENT_TIMEOUT:       
            logging.debug("Event: %s, data: %s" % (self.event_text(typ),data))  
            if typ == gp.GP_EVENT_FILE_ADDED:
                fn = os.path.join(data.folder,data.name)
                logging.debug("New file: %s" % fn)
            typ, data = self.camera.wait_for_event(1)

    def get_camera_model(self, camera_config):
        # get the camera model
        OK, camera_model = gp.gp_widget_get_child_by_name(
            camera_config, 'cameramodel')
        if OK < gp.GP_OK:
            OK, camera_model = gp.gp_widget_get_child_by_name(
                camera_config, 'model')
        if OK >= gp.GP_OK:
            camera_model = camera_model.get_value()
        else:
            camera_model = ''
        print(camera_model)
        return camera_model

    def put_camera_capture_preview_mirror(self, camera, camera_config, camera_model):
        if camera_model == 'unknown':
            # find the capture size class config item
            # need to set this on my Canon 350d to get preview to work at all
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                camera_config, 'capturesizeclass')
            print(OK, capture_size_class)
            if OK >= gp.GP_OK:
                # set value
                value = capture_size_class.get_choice(2)
                capture_size_class.set_value(value)
                # set config
                camera.set_config(camera_config)
        else:
            # put camera into preview mode to raise mirror
            ret = gp.gp_camera_capture_preview(camera) # OK, camera_file
            print(ret) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]

    def run(self):
        self.plugged = True
        logging.debug('Camera running')
        while True:
            last_grab = time.time()
            if config.run == False:
                self.stop()
                break
            OK, self.camera_file = gp.gp_camera_capture_preview(self.camera)
            if config.trigger == True:
                config.devices[self.name+str(self.index)] = False
                logging.debug("Gphoto camera triggered")
                self.t = time.time()
                if OK < gp.GP_OK:
                    print('Failed to capture preview')
                self.filename = config.experiment_path+config.status+"/g"+"_"+str(config.count).zfill(4) +"_"+str(self.index)+".png"
                self.q.put( [self.t, self.filename] )
                file_data = self.camera_file.get_data_and_size()
                self.save_frame_q.put( [self.filename, file_data] )
                self.empty_queue()
                config.devices[self.name+str(self.index)] = True

    def stop(self):
        self.camera.exit()
        logging.warning('Dropped connection with camera')
        sys.exit(1)

    def __exit__(self, exc_type, exc_value, traceback) :
        self.stop()