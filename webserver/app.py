# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

from scute import scute
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, g, session
import json
import os
import datetime
import time
import imp # for importing from specific locations
import zipfile

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

    # recoed this user action
    recordUserAction()

    # user message?
    if 'userMessage'  in session:
        userMessage = session['userMessage']
        session.pop('userMessage')
    else:
        userMessage = False

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


    # load from session if avaiable.
    if 'toolsVersion'  in session:
        toolsVersion = session['toolsVersion']

    else:
        toolsVersion = deviceFunctions.trackerConfigVesion(constants.RUNMODE) 
        session['toolsVersion'] = toolsVersion

    hubDateTime = deviceFunctions.systemTime(constants.RUNMODE) 
     

    return {
        "guiVersion": constants.GUI_VERSION,
        "hardwareVersion": constants.DEVICE_HARDWARE_VERSION,
        "toolsVersion": toolsVersion,
        "hubDateTime": hubDateTime,
        "systemIPAddress": systemIPAddress,
        "hubSDSpace": hubSDSpace,
        "timestamp": time.time(),
        "userMessage": userMessage}

horizonSCUTE.registerHook("get_header_data", getHeaderData)


def recordUserAction():
    thisAction = {
        "path": request.path,
        "method": request.method,
        "fullUrl": request.url
    }
    if 'userActions' not in session:
        session['userActions'] = []

    currentActions = session['userActions']
    currentActions.append(thisAction)

    session['userActions'] = currentActions

    return
    


# get list of currently connected devices
def getDevices():

    if request.method == "POST":
        # POST pass in force_update to clear the session field to rescan for device changes
        if 'force_update' in request.form and request.form['force_update'] == 'yes':
            session.pop('scanResults', None)

            session['userMessage'] = {"type": 'success', "message": "Device Scan Complete"}

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

    saveResponse = deviceFunctions.saveDeviceConfig(constants.RUNMODE, deviceID, config)
    #print(saveResponse)

    if 'error' in saveResponse:
        session['userMessage'] = {"type": 'error', "message": "<h3>Error</h3>" + saveResponse['message']}
    else:
        session['userMessage'] = {"type": 'success', "message": "Config Saved for " + str(deviceID)}

    # remove config from session, so it needs loading again.
    session.pop('config' + str(deviceID), None)


horizonSCUTE.registerHook("save_config", saveConfig)


def deleteAndReplaceLog(deviceID):
    print(deviceID)

    eraseResponse = deviceFunctions.eraseLog(constants.RUNMODE, deviceID)
    createResponse = deviceFunctions.createLog(constants.RUNMODE, deviceID)

    if eraseResponse["result"] == "erased" and createResponse["result"] == "created" :
        return str(deviceID) + " - Log erased and replaced with empty log. "

    response = str(deviceID) + " - "
    
    if eraseResponse["result"] != "erased":
        response += "Log erase failed. "
    
    if createResponse["result"] != "created":
        response += "Log create failed. "

    return response


@app.route('/erase_log')
def erase_log():
    devices = request.args.getlist("devices[]")

    print(devices)
    print(type(devices))
    print(len(devices))

    if len(devices) != 0:

        logResults = map(deleteAndReplaceLog, devices)
        logResults = "    \n".join(logResults)

        session['userMessage'] = {"type": 'info', "message": "Erase Log Results: " + logResults}
                
        
    
    return redirect('list')


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



# @app.route('/reset_flash')
# def reset_flash():
#     devices = request.args.getlist("devices[]")
#     if len(devices) == 1:
#         response = deviceFunctions.flashDevice(constants.RUNMODE, devices[0])

#         if response["result"] == "flashed":
#                 usermessage = {"type": "success",  "message": "Device Flashed: " + devices[0]}
#         else:
#                 usermessage = {"type": "error", "message": "Flash failed for " + devices[0] + ". " + response["result"] }

#         return render_template("defaultPage.html", title="Reset Flash Result", userMessage=usermessage, headerData = getHeaderData() )

# @app.route('/gps_ascii')
# def gps_ascii():
#     devices = request.args.getlist("devices[]")
#     if len(devices) == 1:
#         return deviceFunctions.dummyResponse(constants.RUNMODE, devices[0], "Apply GPS ASCII")


@app.route('/erase_tag')
def erase_tag():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.eraseDevice(constants.RUNMODE, devices[0])

        if response["result"] == "erased":

                session['userMessage'] = {"type": 'info', "message": "Device Erased: " + devices[0]}
        else:
                session['userMessage'] = {"type": 'error', "message": "Erase failed for " + devices[0]}
                
        return redirect('list')



@app.route('/view_log')
def view_log():
    devices = request.args.getlist("devices[]")
    downloadNew = request.args.get("new") # returns 'None' or the value

    print (downloadNew)
    if len(devices) == 1:

        logData =  deviceFunctions.viewLatestLogData(constants.RUNMODE, devices[0], downloadNew)

        if downloadNew == 'yes':
            session['userMessage'] = {"type": 'info', "message": "Log Imported"}

        return render_template("view_log.html", title="Latest Log for " + devices[0], headerData = getHeaderData(), logData=logData, device=devices[0])



@app.route('/delete_log')
def selete_log():
    devices = request.args.getlist("devices[]")
    deleteKey = request.args.getlist("key")

    deleteLogResult = deviceFunctions.deleteLogData(constants.LOG_DATA_LOCAL_LOCATION, devices[0], deleteKey)

    if len(devices) == 1:

        logData =  deviceFunctions.viewLatestLogData(constants.RUNMODE, devices[0], False)
        session['userMessage'] = {"type": 'info', "message": "Log Deleted: " + str(deleteKey[0])}

        return render_template("view_log.html", title="Latest Log for " + devices[0], headerData = getHeaderData(), logData=logData, device=devices[0])



@app.route('/downloadLog')
def downloadLogFile ():
    fileName = request.args.getlist("file")[0]
    directory = request.args.getlist("device")[0]
    root = constants.LOG_DATA_LOCAL_LOCATION

    return send_from_directory(root + directory, fileName , as_attachment=True, attachment_filename=directory+ "_" + fileName.replace(".bin", ".binary") )

@app.route('/download_file')
def downloadFile ():  
    # this can be extended for other file types.
    # don't allow full file specificaiton
    
    allowedTypes = ['preset']

    fileName = request.args.getlist("file")[0]
    fileType = request.args.getlist("type")[0]


    if fileType in allowedTypes:
        if fileType == 'preset':
            fileLocation = "presets/" + fileName + '.json'

            return send_from_directory('', fileLocation , as_attachment=True, attachment_filename=fileName+'.preset.json' )
    
    # still here?  error.
    session['userMessage'] = {"type": 'error', "message": "User tried to download invalid file." }
    
    return redirect('list')
    


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


def getFileNamesForDevice(deviceID):

    # get config from device, get it's filename.
    deviceFunctions.getDeviceConfig(constants.RUNMODE, deviceID, True)
    latestConfigFilename = deviceFunctions.isConfigAlreadyOnLocal(deviceID)

    # get logs from device, construct filenames
    logData =  deviceFunctions.viewLatestLogData(constants.RUNMODE, deviceID, 'yes')
    logroot = constants.LOG_DATA_LOCAL_LOCATION + deviceID + '/' + logData['latestLogDateTime'].replace(' ', '_')

    deviceReturn = {deviceID: {'config': latestConfigFilename, 'logJson': logroot + '.json', 'logBinary': logroot + '.bin'}}
    
    return deviceReturn


def makeZip(deviceFilenameArray):

    # the zip file
    dateTime = deviceFunctions.systemTime(constants.RUNMODE)
    zipFileName = constants.DOWNLOAD_DATA_LOCATION + constants.DOWNLOAD_DATA_FILEPREFIX + '_' + dateTime.replace(' ', '_') + '.zip'

    # delete existing zip file if any.
    if os.path.exists(zipFileName):
        os.remove(zipFileName)

    zipf = zipfile.ZipFile(zipFileName,'w', zipfile.ZIP_DEFLATED)

    for deviceData in deviceFilenameArray:

        thisDevice = deviceData.keys()[0]

        zipf.write(deviceData[thisDevice]['config'])
        zipf.write(deviceData[thisDevice]['logJson'])
        zipf.write(deviceData[thisDevice]['logBinary'])

    return zipFileName


@app.route('/download_data')
def downloadDataZip ():

    devices = request.args.getlist("devices[]")
    if len(devices) == 0:
        #TODO
        return "Invalid Device ID"

    # for each device passed in:
        # pull latest log from device
        # pull config from device
        # add to zip output (local temp save?)
        # return the zip file as download.

    filenamesToZip = map(getFileNamesForDevice, devices)

    zipFilename = makeZip(filenamesToZip)

    return send_from_directory('', zipFilename , as_attachment=True )


@app.route('/sync_clock')
def syncClock():
        
    toTime = request.args.getlist('clock_sync')[0]
    passTo = request.args.getlist('passTo')[0]
    print("set the clock to " + toTime + ' ' + passTo)
    deviceFunctions.syncHubToTime(constants.RUNMODE, toTime)

    # set user message
    session['userMessage'] = {"type": 'success', "message": "Hub clock updated to "+toTime }
    
    return redirect(passTo)

@app.route('/my_actions')
def userActions():

    if 'userActions' in session:
        return json.dumps(session['userActions'])
    else: 
        return 'None'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

