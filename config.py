import os


serial = False # Will you be using an Arduino for ADC acquisition ?
continuous_serial = False #If True, Arduino data will be constantly logged as well as when a picture is grabbed
serial_port = "/dev/ttyACM0"
serial_baudrate = 115200

opencv = True # Will you be using a webcam ?
cvexclude = 2 # Put here the index of the front facing webcam if on a laptop (run with -1 to find it)
DSLR = True # Will you be using a gphoto2 compatible camera ?
DSLR_continuous = True # If True will use fast mode low resolution

timestep = 1
experiment_path = os.getcwd()+"/Dummy_experiment/"


# No need to change these variables
status = "experiment"
run = True
preview = False
trigger = False
framebuffer = None
devices = {}
count = 0
data_export_script = os.getcwd()+"/export_data.py"