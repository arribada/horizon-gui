def init():
    global dummy_Responses
    dummy_Responses = {
        "VERSION": "Version: Debug Mode...",
        "SCAN": [{
            "friendlyName": "Tony Tag",
            "connection":
            "USB",
            "batteryLevel":
            50,
            "logFileSize":
            123456,
            "deviceID":
            "1111111111111111",
            "configVerison":
            10,
            "sensorsEnabled":
            ["gps", "pressure", "saltwater", "accelerometer"],
            "connectionID":
            "usb03",
            "firmwareVersion":
            4,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/1111111111111111'>Config</a>" 
        }, {
            "friendlyName": "Timmy Tag",
            "connection": "USB",
            "batteryLevel": 100,
            "logFileSize": 123456,
            "deviceID": "2222222222222222",
            "configVerison": 8,
            "sensorsEnabled": ["gps", "saltwater", "accelerometer"],
            "connectionID": "usb01",
            "firmwareVersion": 3,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/2222222222222222'>Config</a>" 
        }, {
            "friendlyName": "Thomasina Tag",
            "connection": "Bluetooth",
            "batteryLevel": 35,
            "logFileSize": 123456,
            "deviceID": "333333333333",
            "configVerison": 10,
            "sensorsEnabled": ["gps"],
            "connectionID": "bt01",
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/333333333333'>Config</a>" 
        }, {
            "friendlyName": "Tiny Tag",
            "connection": "Bluetooth",
            "batteryLevel": 35,
            "logFileSize": 123456,
            "deviceID": "666666666666666",
            "configVerison": 10,
            "sensorsEnabled": ["gps"],
            "connectionID": "bt02",
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/666666666666666'>Config</a>" 
        }, {
            "friendlyName": "Tobias Tag",
            "connection": "USB",
            "batteryLevel": 35,
            "logFileSize": 123456,
            "deviceID": "444444444444",
            "configVerison": 10,
            "sensorsEnabled": ["gps"],
            "connectionID": "usb02",
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/444444444444'>Config</a>" 

        }, {
            "friendlyName": "Tabatha Tag",
            "connection": "USB",
            "batteryLevel": 35,
            "logFileSize": 123456,
            "deviceID": "5555555555555",
            "configVerison": 10,
            "sensorsEnabled": ["gps"],
            "connectionID": "usb04",
            "firmwareVersion": 4,
            "logFileType": "LINEAR",
            "edit": "<a href='/config/get/5555555555555'>Config</a>" 
        }
        ],
        "STATUS": {
            "cfg_version": 4,
            "ble_fw_version": 65704,
            "fw_version": 10,
            "debugMode": "On"
        },
        "CONFIG_FILE": "dummy_data/dummy_config.json"
    }