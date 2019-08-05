# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

from scute import scute
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, g
import json
import os
import datetime

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
    if deviceID != config['system']['deviceIdentifier']:
        g.redirect = '/'

    deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)

horizonSCUTE.registerHook("save_config", saveConfig)


@app.route('/erase_log')
def erase_log():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.eraseLog(constants.RUNMODE, devices[0])

        if response["result"] == "erased":
                usermessage = {"type": "success",  "message": "Log erased for " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Log erase failed for " + devices[0] + ". " + response["result"] }

        return render_template("defaultPage.html", title="Erase Log Result", userMessage=usermessage )


def scanDirectory(target):

    print("Scanning " + target)

    if not os.path.exists(target):
        return "There are files in this directory."

    pathContent = os.listdir(target)
   
    returnFiles = []

    for file in pathContent:
        fileName = file.split(".")
        returnFiles.append({"fileName": file, "fileSizeKb": os.path.getsize(target + "/" + file) / 10000, "fileDate": fileName[0], "fileType": fileName[1]})

    return returnFiles

@app.route('/uploads')
def uploads():
        # this is on hold for current release
        return render_template("uploads.html", title="Upload Manager" , gps_almanacFiles=scanDirectory("upload/gps_almanac"),  firmwareFiles=scanDirectory("upload/firmware"))
  

def getAlmanacList():

    almanacPath = "upload/gps_almanac"

    if not os.path.exists(almanacPath):
        print(almanacPath + " not there")
        return {}

    pathContent = os.listdir(almanacPath)
   
    returnFiles = {}

    for file in pathContent:
        fileName = file.split(".")
        returnFiles[fileName[0]] = file
    
    return returnFiles


horizonSCUTE.registerHook("get_list__gps_almanacFiles", getAlmanacList)


@app.route('/gps_almanac')
def gps_almanac():
    print("gps_almanac")


    devices = request.args.getlist("devices[]")
    fileToApply = request.args.get("value")
    if len(devices) == 1:
        response = deviceFunctions.writeGPSAlmanacToDevice(constants.RUNMODE, devices[0], fileToApply )

        if response["result"] == "flashed":
                usermessage = "Device " + devices[0] + " GPS Almanac Uploaded."
        else:
                usermessage = "GPS Almanac Upload failed for " + devices[0] + ". " + response["result"]

        return render_template("defaultPage.html", title="GPS Almanac Upload Result", userMessage=usermessage )


    # if request.method == 'POST':
    #         print(request.args)
    #         # check for post data and deal with it...
    #         return render_template("gps_almanac.html", title="GPS Almanac for " + devices[0], device=devices[0], gps_almanacFiles=scanDirectory("upload/gps_almanac"))


@app.route('/reset_flash')
def reset_flash():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.flashDevice(constants.RUNMODE, devices[0])

        if response["result"] == "flashed":
                usermessage = {"type": "success",  "message": "Device Flashed: " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Flash failed for " + devices[0] + ". " + response["result"] }

        return render_template("defaultPage.html", title="Reset Flash Result", userMessage=usermessage )


@app.route('/erase_tag')
def erase_tag():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.eraseDevice(constants.RUNMODE, devices[0])

        if response["result"] == "erased":
                usermessage = {"type": "success",  "message": "Device Erased: " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Erase failed for " + devices[0] + ". " + response["result"] }

        return render_template("defaultPage.html", title="Erase Device Result", userMessage=usermessage )



@app.route('/gps_ascii')
def gps_ascii():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Apply GPS ASCII")


@app.route('/view_log')
def view_log():
    devices = request.args.getlist("devices[]")
    downloadNew = request.args.get("new") # returns 'None' or the value

    print (downloadNew)
    if len(devices) == 1:

        logData =  deviceFunctions.vewLatestLogData(constants.RUNMODE, devices[0], downloadNew)

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


@app.route('/downloadLog')
def downloadLogFile ():
    fileName = request.args.getlist("file")[0]
    directory = request.args.getlist("device")[0]
    root = constants.LOG_DATA_LOCAL_LOCATION

    return send_from_directory(root + directory, fileName , as_attachment=True, attachment_filename=directory+ "_" + fileName.replace(".bin", ".binary") )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

