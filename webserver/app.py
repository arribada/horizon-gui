# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

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
        "dashboardSchema": "dashboardSchema.json"
    }
#instantiate SCUTE
horizonSCUTE = scute(options, app)

# get list of currnetly connected devices
def getDevices():
    return deviceFunctions.scanForAttachedDevices(constants.RUNMODE, constants.SCAN_USB, constants.SCAN_BLUETOOTH)    

horizonSCUTE.registerHook("get_devices", getDevices)


# get the report data for one device
def getReportFields(deviceID):
    return deviceFunctions.getDeviceReport(constants.RUNMODE, deviceID)    

horizonSCUTE.registerHook("get_report_fields", getReportFields)


# read the config for one device
def readConfig(deviceID):

    # get device config
    config = deviceFunctions.getDeviceConfig(constants.RUNMODE, deviceID)
    # convert to flat scructure
    config = horizonSCUTE.flattenJSON(config)

    return config

horizonSCUTE.registerHook("read_config", readConfig)



# save config for one device
def saveConfig(deviceID, config):

    # indent fields into categories
    config = horizonSCUTE.expandJSON(config)
    #save config
    deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)

horizonSCUTE.registerHook("save_config", saveConfig)



# andle export requests - either for one device or multiple.
@app.route('/export')
def export():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
            return deviceFunctions.receiveTrackerLogData(constants.RUNMODE, devices[0])
    else:
        #TODO
        return "<h1>Functionality to be confirmed for multiple exports.</h1>"

    




    