# Example file

from scute import scute
from flask import Flask, request
import json

## project functions
import deviceFunctions

app = Flask(__name__)

RUNMODE = "dummy"

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
    }

test = scute(options, app)

def getDevices():
    return deviceFunctions.scanForAttachedDevices(RUNMODE, False, False)    


test.registerHook("get_devices", getDevices)

def getFields(deviceID):
    return deviceFunctions.getDeviceReport(RUNMODE, deviceID)    


test.registerHook("get_report_fields", getFields)

# def getFriendlyName(deviceID):
#     return deviceID + "FRIENDLY"

# test.registerHook("get_report_field__friendlyName", getFriendlyName)

def saveConfig(deviceID, config):
    deviceFunctions.saveDeviceConfig(RUNMODE, deviceID, config)

test.registerHook("save_config", saveConfig)

def readConfig(deviceID):

    data = deviceFunctions.getDeviceConfig(RUNMODE, deviceID)
    
    return data

test.registerHook("read_config", readConfig)

@app.route('/export/<device>')
def viewLog(device):

    return deviceFunctions.receiveTrackerLogData(RUNMODE, device)
    