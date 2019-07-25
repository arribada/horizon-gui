# set to "dummy" to run without PI or devices
RUNMODE = "pi"
#RUNMODE = "dummy"

DUMMY_RESPONSES = "dummy_data/dummyResponses.json"

# the toolset command name
TRACKER_CONFIG = "tracker_config"

# used in a numbe of places
NO_TAG_TEXT = "No Device Detected."

# when not in dummy mode, should we scan for USB devices?
SCAN_USB= True

# when not in dummy mode, should we scan for Bluetooth devices?
SCAN_BLUETOOTH = False

CONFIG_LOCAL_LOAD_LOCATION = "config/" # can separate these if needed...
CONFIG_LOCAL_SAVE_LOCATION = "config/" 

LOG_DATA_LOCAL_LOCATION = "log_data/" # can separate these if needed...

# for uploads - TBC
ALLOWED_EXTENSIONS = set(['txt', 'gif'])
UPLOAD_FOLDERS =  {"config": "/uploads/config", "firmware": "/uploads/firmware" }

FRIENDLY_NAME_ACTIVE = False

#LOGGING_LEVEL = "none"
LOGGING_LEVEL = "verbose"



