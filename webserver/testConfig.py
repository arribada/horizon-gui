def init():
    global runSettings
    runSettings = {
        "RUNMODE": 'dummy',  # or 'full' for running dummy tools with no hardware
        "TRACKER_CONFIG_VERSION": "tracker_config",

        "SCAN_USB": False,
        "SCAN_BLUETOOTH": False,

        "ALLOWED_EXTENSIONS": set(['txt', 'gif']),
        "UPLOAD_FOLDERS": {"config": "/uploads/config", "firmware": "/uploads/firmware" },
        "NO_TAG_TEXT": 'No Device Detected.',
        "DUMMY_RESPONSE_MODULE": "dummyResponses1"
    }