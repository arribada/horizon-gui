# set to "dummy" to run without PI or devices
RUNMODE = "pi"
DUMMY_RESPONSES = "dummy_data/dummyResponses.json"

# the toolset command name
TRACKER_CONFIG = "tracker_config"

# used in a numbe of places
NO_TAG_TEXT = "No Device Detected."

# when not in dummy mode, should we scan for USB devices?
SCAN_USB= True

# when not in dummy mode, should we scan for Bluetooth devices?
SCAN_BLUETOOTH = False

CONFIG_LOCAL_LOAD_LOCATION = "config/from_tag/"
CONFIG_LOCAL_SAVE_LOCATION = "config/to_tag/"

# for uploads - TBC
ALLOWED_EXTENSIONS = set(['txt', 'gif'])
UPLOAD_FOLDERS =  {"config": "/uploads/config", "firmware": "/uploads/firmware" }

FRIENDLY_NAME_ACTIVE = False



