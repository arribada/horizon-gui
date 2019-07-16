# Example file

from scute import scute
from flask import Flask, request
import json

## project functions
import deviceFunctions
import constants

app = Flask(__name__)

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
    }

horizonSCUTE = scute(options, app)

def getDevices():
    return deviceFunctions.scanForAttachedDevices(constants.RUNMODE, constants.SCAN_USB, constants.SCAN_BLUETOOTH)    


horizonSCUTE.registerHook("get_devices", getDevices)

def getFields(deviceID):
    return deviceFunctions.getDeviceReport(constants.RUNMODE, deviceID)    


horizonSCUTE.registerHook("get_report_fields", getFields)

# def getFriendlyName(deviceID):
#     return deviceID + "FRIENDLY"

# horizonSCUTE.registerHook("get_report_field__friendlyName", getFriendlyName)

def saveConfig(deviceID, config):

    config = horizonSCUTE.expandJSON(config)

    deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)

horizonSCUTE.registerHook("save_config", saveConfig)

def readConfig(deviceID):

    config = deviceFunctions.getDeviceConfig(constants.RUNMODE, deviceID)
    print(config)

    config = horizonSCUTE.flattenJSON(config)
    print(config)
    return config

horizonSCUTE.registerHook("read_config", readConfig)


@app.route('/export')
def export():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
            return deviceFunctions.receiveTrackerLogData(constants.RUNMODE, devices[0])
    else:
        #TODO
        return "Functionality to be confirmed for multiple exports."

    




    