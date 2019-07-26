# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

from scute import scute
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import json
import os

## project functions
import deviceFunctions
import constants

app = Flask(__name__)

# questions for filip
# need to horizonSCUTE = scute(options, app) here AND deviceFunctions..  how do I share SCUTE?
# the calls take a while, I'd like to use session data across modules so not always need to load config for example.

#app.secret_key = "super secret key"

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
    config = horizonSCUTE.flattenJSON(config['result'])
    return config

horizonSCUTE.registerHook("read_config", readConfig)



# save config for one device
def saveConfig(deviceID, config):
    # indent fields into categories
    config = horizonSCUTE.expandJSON(config)
    #save config
    deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)

horizonSCUTE.registerHook("save_config", saveConfig)


@app.route('/erase_log')
def erase_log():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Erase Log")

@app.route('/update_gps_almanac')
def update_gps_almanac():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Update GPS Almanac")

@app.route('/reset_flash')
def reset_flash():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Reset Flash")

@app.route('/apply_gps_ascii')
def apply_gps_ascii():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Apply GPS ASCII")


@app.route('/view_log')
def view_log():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        logData =  deviceFunctions.vewLatestLogData(constants.RUNMODE, devices[0])

        return render_template("view_log.html", title="Latest Log for " + devices[0], logData=logData, device=devices[0])



# andle export requests - either for one device or multiple.
@app.route('/request_log')
def request_log():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.receiveTrackerLogData(constants.RUNMODE, devices[0])
    else:
        #TODO
        return "<h1>Functionality to be confirmed for multiple exports.</h1>"


@app.route('/download')
def downloadFile ():
    fileName = request.args.getlist("file")[0]
    directory = request.args.getlist("device")[0]
    root = constants.LOG_DATA_LOCAL_LOCATION

    return send_from_directory(root + directory, fileName , as_attachment=True, attachment_filename=directory+ "_" + fileName.replace(".bin", ".binary") )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)



    