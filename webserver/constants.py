
# GUI version nuber.  Must update manually
GUI_VERSION = "v0.1.0"

# device tool version / directory
DEVICE_HARDWARE_VERSION = "v2.0"  # for firmware 11 hardware 2
#DEVICE_HARDWARE_VERSION = "v3.0" # for firmware ?? hardware 3

# set to "dummy" to run without PI or devices
RUNMODE = "pi"
#RUNMODE = "dummy"

DUMMY_RESPONSES = "dummy_data/dummyResponses.json"

# the toolset command name
TRACKER_CONFIG = "tracker_config"

# number of data blocks in value config
VALID_CONFIG_DATA_BLOCKS = 8

# used in a numbe of places
NO_TAG_TEXT = "No Device Detected."

# when not in dummy mode, should we scan for USB devices?
SCAN_USB= True

# Bluetooth is not yet implemented. when not in dummy mode, should we scan for Bluetooth devices?
SCAN_BLUETOOTH = False

LOG_DATA_LOCAL_LOCATION = "log_data/" # can separate these if needed...

CONFIG_DATA_LOCAL_LOCATION = "config/" 

DOWNLOAD_DATA_LOCATION = "tmp/"
DOWNLOAD_DATA_FILEPREFIX = "HorizonData"


#LOGGING_LEVEL = "none"
LOGGING_LEVEL = "verbose"

CONFIG_FILE_EXTENSION = 'config'
CONFIG_FILE_NUMBER_TO_KEEP = 10

BATTERY_ERROR_TOOLTIP = "Battery Error returned. Try charging battery or replacing"
BATTERY_ERROR_TEXT = "Battery Error"



