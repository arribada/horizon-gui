def init():
    global runSettings
    runSettings = {
        "RUNMODE": 'offline',  # or 'PI' for running dummy tools with no hardware
        "TRACKER_CONFIG_VERSION": "tracker_config",

        "SCAN_USB": False,
        "SCAN_BOOTHTOOTH": False,

        "ALLOWED_EXTENSIONS": set(['txt']),
        "UPLOAD_FOLDER": '/uploads',
        "NO_TAG_TEXT": 'No Device Detected.'
    }