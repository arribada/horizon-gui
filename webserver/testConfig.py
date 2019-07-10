def init():
    global runSettings
    runSettings = {
        "RUNMODE": 'dummy',  # or 'full' for running dummy tools with no hardware
        "TRACKER_CONFIG_VERSION": "tracker_config",

        "SCAN_USB": False,
        "SCAN_BLUETOOTH": False,

        "ALLOWED_EXTENSIONS": set(['txt']),
        "UPLOAD_FOLDER": '/uploads',
        "NO_TAG_TEXT": 'No Device Detected.',
        "DUMMY_RESPONSE_MODULE": "dummyResponses1"
    }