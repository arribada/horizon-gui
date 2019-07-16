# set to "dummy" to run without PI or devices
RUNMODE = "dummy"

# the toolset command name
TRACKER_CONFIG = "tracker_config"

# used in a numbe of places
NO_TAG_TEXT = "No Device Detected."

# when not in dummy mode, should we scan for USB devices?
SCAN_USB= False

# when not in dummy mode, should we scan for Bluetooth devices?
SCAN_BLUETOOTH = False

# for uploads - TBC
ALLOWED_EXTENSIONS = set(['txt', 'gif'])
UPLOAD_FOLDERS =  {"config": "/uploads/config", "firmware": "/uploads/firmware" }

