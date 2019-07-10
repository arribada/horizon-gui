def init():
    global responses
    responses = {
        "VERSION":
        "Version: Debug Mode...",
        "SCAN": [
            {
            "connection": "USB",
            "connectionID": 1,
            "deviceID": "1111111111111111",
            "friendlyName": "Tony Tag",
            "batteryLevel": 50,
            "configVerison": 10,
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "logFileSize": 123456,
            "sensorsEnabled": ["gps", "pressure", "saltwater", "accelerometer"]
            },
            {
            "connection": "USB",
            "connectionID": 2,
            "deviceID": "2222222222222222",
            "friendlyName": "Timmy Tag",
            "batteryLevel": 100,
            "configVerison": 8,
            "firmwareVersion": 3,
            "logFileType": "LINEAR",
            "logFileSize": 123456,
            "sensorsEnabled": ["gps", "saltwater", "accelerometer"]
            },
            {
            "connection": "Bluetooth",
            "connectionID": 2,
            "deviceID": "333333333333",
            "friendlyName": "Thomasina Tag",
            "batteryLevel": 35,
            "configVerison": 10,
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "logFileSize": 123456,
            "sensorsEnabled": ["gps"]
            }
            ],
            "STATUS": {"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10, "debugMode": "On"},
            "CONFIG_FILE": "dummy_data/dummy_config.json"
    }