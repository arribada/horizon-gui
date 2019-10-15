# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

from scute import scute
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, g, session
import json
import os
import datetime
import time
import imp # for importing from specific locations

## project functions
import constants
#import deviceFunctions
deviceFunctions = imp.load_source('deviceFunctions', 'hardwareVersion/' + constants.DEVICE_HARDWARE_VERSION + '/deviceFunctions.py')

app = Flask(__name__)
app.secret_key = os.urandom(24)

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
        "helpInfo": "helpInformation.json"
    }
#instantiate SCUTE
horizonSCUTE = scute(options, app)

def getIndexData():

    # session management... Only one user allowed - flag it.
    accessAllowed = False
    if 'activeUser' not in session:
        accessAllowed = True 
        session['activeUser'] = "this user"
        usermessage = {"type": "success",  "message": "OK"}
    else:
        accessAllowed = True # this needs to be false, but also need specific user check. 
        usermessage = {"type": "error",  "message": "Hub In Use."}

    return {"accessAllowed": accessAllowed, "usermessage": usermessage}


horizonSCUTE.registerHook("get_index_data", getIndexData)


def getHeaderData():


    # load from session if avaiable.
    if 'systemIPAddress'  in session:
        systemIPAddress = session['systemIPAddress']

    else:
        systemIPAddress = deviceFunctions.systemIPAddress(constants.RUNMODE) 
        session['systemIPAddress'] = systemIPAddress

    if 'hubSDSpace'  in session:
        hubSDSpace = session['hubSDSpace']

    else:
        hubSDSpace = deviceFunctions.hubSDSpace(constants.RUNMODE) 
        session['hubSDSpace'] = hubSDSpace


    hubDateTime = deviceFunctions.systemTime(constants.RUNMODE) 
     

    return {
        "guiVersion": constants.GUI_VERSION,
        "hardwareVersion": constants.DEVICE_HARDWARE_VERSION,
        "hubDateTime": hubDateTime,
        "systemIPAddress": systemIPAddress,
        "hubSDSpace": hubSDSpace,
        "timestamp": time.time()}

horizonSCUTE.registerHook("get_header_data", getHeaderData)


# get list of currently connected devices
def getDevices():

    # pass in ?force_update to clear the session field
    if len(request.args.getlist("force_update")) != 0:
        session.pop('scanResults', None)

    if 'scanResults' in session:
        scanResults = session['scanResults']

    else:
        scanResults = deviceFunctions.scanForAttachedDevices(constants.RUNMODE, constants.SCAN_USB, constants.SCAN_BLUETOOTH)  
        session['scanResults'] = scanResults


    return scanResults  

horizonSCUTE.registerHook("get_devices", getDevices)


# get the report data for one device
def getReportFields(deviceID):

    # pass in ?force_update to clear the session field
    if len(request.args.getlist("force_update")) != 0:
        session.pop('report_' + str(deviceID), None)
        print("Clear session report for "+ str(deviceID))

    if 'report_' + str(deviceID) in session:
        thisReport = session['report_' + str(deviceID)]
        print("Load session report for "+ str(deviceID))

    else:
        thisReport = deviceFunctions.getDeviceReport(constants.RUNMODE, deviceID)  
        session['report_' + str(deviceID)] = thisReport
        print("Load device report for "+ str(deviceID))

    print(thisReport)
    return thisReport        

horizonSCUTE.registerHook("get_report_fields", getReportFields)


# read the config for one device
def readConfig(deviceID):

    # always load from device when this is called...  This saves a new local file.
    config = deviceFunctions.getDeviceConfig(constants.RUNMODE, deviceID, True)
    
    # pop it into session in case needed later.
    session['config' + str(deviceID)] = config

    # make single depth
    config = horizonSCUTE.flattenJSON(config['result'])

    config['local.friendlyName'] = deviceFunctions.getFriendlyName(deviceID)
    
    return config

horizonSCUTE.registerHook("read_config", readConfig)



# save config for one device
def saveConfig(deviceID, config):
    # indent fields into categories
    config = horizonSCUTE.expandJSON(config)

    deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)

    # remove config from session, so it needs loading again.
    session.pop('config' + str(deviceID), None)


horizonSCUTE.registerHook("save_config", saveConfig)


@app.route('/erase_log')
def erase_log():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        eraseResponse = deviceFunctions.eraseLog(constants.RUNMODE, devices[0])
        createResponse = deviceFunctions.createLog(constants.RUNMODE, devices[0])

        if eraseResponse["result"] == "erased" and createResponse["result"] == "created" :
                usermessage = {"type": "success",  "message": "Log erased and created for " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Log erase failed for " + devices[0] + ". " + eraseResponse["result"]  + "  " + createResponse["result"] }

        return render_template("defaultPage.html", title="Erase Log Result", headerData = getHeaderData(), userMessage=usermessage )


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
        return render_template("uploads.html", title="Upload Manager" , headerData = getHeaderData(), gps_almanacFiles=scanDirectory("upload/gps_almanac"),  firmwareFiles=scanDirectory("upload/firmware"))

@app.route('/admin_console')
def admin_console():
        # this is on hold for current release
        return render_template("adminConsole.html", title="Admin Console",headerData = getHeaderData() )
  

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

        return render_template("defaultPage.html", title="GPS Almanac Upload Result", headerData = getHeaderData(), userMessage=usermessage )


@app.route('/reset_flash')
def reset_flash():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.flashDevice(constants.RUNMODE, devices[0])

        if response["result"] == "flashed":
                usermessage = {"type": "success",  "message": "Device Flashed: " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Flash failed for " + devices[0] + ". " + response["result"] }

        return render_template("defaultPage.html", title="Reset Flash Result", userMessage=usermessage, headerData = getHeaderData() )


@app.route('/erase_tag')
def erase_tag():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.eraseDevice(constants.RUNMODE, devices[0])

        if response["result"] == "erased":
                usermessage = {"type": "success",  "message": "Device Erased: " + devices[0]}
        else:
                usermessage = {"type": "error", "message": "Erase failed for " + devices[0] + ". " + response["result"] }

        return render_template("defaultPage.html", title="Erase Device Result", headerData = getHeaderData(), userMessage=usermessage )



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

        return render_template("view_log.html", title="Latest Log for " + devices[0], headerData = getHeaderData(), logData=logData, device=devices[0])



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

@app.route('/download_config')
def downloadConfigFile ():

    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        device = devices[0]
        
    else:
        #TODO
        return "Invalid Device ID"
    
    root = constants.CONFIG_DATA_LOCAL_LOCATION

    fileList = os.listdir(root + device)
    fileList.sort()

    return send_from_directory(root + device, fileList[len(fileList)-1] , as_attachment=True )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

