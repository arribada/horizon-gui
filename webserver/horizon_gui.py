# Horizon Tag Manager using SCUTE
# see https://github.com/Octophin/scute for more info.

from scute import scute
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, g, session
import json
import os
import datetime
from datetime import datetime, date
import time
import imp # for importing from specific locations
import zipfile
from flask_babel import gettext, ngettext
import csv
import sys
from pathlib import Path

## project functions
import constants
import localisation
#import deviceFunctions
deviceFunctions = imp.load_source('deviceFunctions', 'hardwareVersion/' + constants.DEVICE_HARDWARE_VERSION + '/deviceFunctions.py')

app = Flask(__name__)
app.secret_key = os.urandom(24)

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "scriptsDirectory": "scripts",
        "presetsDirectory": "presets",
        "helpInfo": "helpfiles/index.md"
    }
#instantiate SCUTE
horizonSCUTE = scute(options, app)

def getSystemInfo():

    # recoed this user action
    recordUserAction()

    # is there a user message in session? extract it for display and remove it from session.
    if 'userMessage' in session:
        userMessage = session['userMessage']
        userMessage['message']  = gettext(userMessage['message'])
        session.pop('userMessage')
    else:
        userMessage = False

    now = datetime.now()

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

    # page titles from localisation?
    pageTitle = None
    if request.endpoint in localisation.pageTitles:
        pageTitle = localisation.pageTitles[request.endpoint]
        pageTitle = gettext(pageTitle)



    # load from session if avaiable.
    latestScan = ''
    if 'scanResultsDateTime'  in session:
        latestScan = session['scanResultsDateTime']

    return {
        "guiVersion": constants.GUI_VERSION,
        "hardwareVersion": constants.DEVICE_HARDWARE_VERSION,
        "toolsVersion": toolsVersion,
        "hubDateTime": hubDateTime,
        "systemIPAddress": systemIPAddress,
        "hubSDSpace": hubSDSpace,
        "timestamp": time.time(),
        "userMessage": userMessage,
        "pageTitle": pageTitle,
        "latestScan": latestScan,
        "scuteVersion": horizonSCUTE.getSCUTEVersion(),
        "currentDateTime": now.strftime("%c")
        }

horizonSCUTE.registerHook("get_system_info", getSystemInfo)


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
            session.pop('scanResultsDateTime', None)

            session['userMessage'] = {"type": 'success', "message": "Device Scan Complete."}

    if 'scanResults' in session:
        scanResults = session['scanResults']

    else:
        scanResults = deviceFunctions.scanForAttachedDevices(constants.RUNMODE, constants.SCAN_USB, constants.SCAN_BLUETOOTH)

        session['scanResults'] = scanResults

        session['scanResultsDateTime'] = deviceFunctions.currentDateTimeDisplay("%a %w %b %Y, %H:%M:%S")

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

    if len(config['result'].keys()) == constants.VALID_CONFIG_DATA_BLOCKS:

        # pop it into session in case needed later.
        session['config' + str(deviceID)] = config

    else:
        # flag scute that the config is wrong.
        config['result']['invalidConfigDetected'] = True


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

    if 'error' in saveResponse:
        response = {"type": 'error', "message": "<h3>Error</h3>" + saveResponse['error']}
    else:
        response = {"type": 'success', "message": "Config Saved for <strong>" + str(deviceID) + "</strong>"}

    # remove config from session, so it needs loading again.
    session.pop('config' + str(deviceID), None)
    session.pop('report_' + str(deviceID), None)

    return response


horizonSCUTE.registerHook("save_config", saveConfig)


def deleteAndReplaceLog(deviceID):

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

    # print(devices)
    # print(type(devices))
    # print(len(devices))

    if len(devices) != 0:

        logResults = map(deleteAndReplaceLog, devices)
        logResults = "    \n".join(logResults)

        session['userMessage'] = {"type": 'info', "message": "Erase Log Results: <strong>" + logResults + "</strong>"}



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



@app.route('/erase_tag')
def erase_tag():
    devices = request.args.getlist("devices[]")
    if len(devices) == 1:
        response = deviceFunctions.eraseDevice(constants.RUNMODE, devices[0])


        if response["result"] == "erased":

                # forget device
                deviceFunctions.forgetDevice(devices[0])
                # remove config from session, so it needs loading again.
                session.pop('config' + str(devices[0]), None)
                session.pop('report_' + str(devices[0]), None)

                session['userMessage'] = {"type": 'info', "message": "Device Erased: <strong>" + devices[0] + "</strong>"}

        else:
                session['userMessage'] = {"type": 'error', "message": "Erase failed for <strong>" + devices[0]+ "</strong>"}

        return redirect('list')



@app.route('/view_log')
def view_log():
    devices = request.args.getlist("devices[]")

    if len(devices) == 1:

        downloadNew = request.args.get("new") # returns 'None' or the value
        csv_ready = request.args.get("csv_ready") # returns 'None' or the value
        csv_location = request.args.get("csv_location") # returns 'None' or the value

        logData =  deviceFunctions.viewLatestLogData(constants.RUNMODE, devices[0], downloadNew)

        if downloadNew == 'yes':
            session['userMessage'] = {"type": 'info', "message": "Log Imported"}

        if csv_ready:
            session['userMessage'] = {"type": 'info', "message": "CSV Files available for download"}


        return render_template("content/view_log.html", title="Latest Log for " + devices[0], systemInfo = getSystemInfo(), logData=logData, device=devices[0], csv_ready=csv_ready, csv_location=csv_location )



@app.route('/delete_log')
def selete_log():
    devices = request.args.getlist("devices[]")
    deleteKey = request.args.getlist("key")

    deleteLogResult = deviceFunctions.deleteLogData(constants.LOG_DATA_LOCAL_LOCATION, devices[0], deleteKey)

    if len(devices) == 1:

        logData =  deviceFunctions.viewLatestLogData(constants.RUNMODE, devices[0], False)
        session['userMessage'] = {"type": 'info', "message": "Log Deleted: <strong>" + str(deleteKey[0])+"</strong>"}

        return render_template("content/view_log.html", title="Latest Log for " + devices[0], systemInfo = getSystemInfo(), logData=logData, device=devices[0])



@app.route('/downloadLog')
def downloadLogFile ():

    # switch between raw log data and csv data
    type = request.args.get("type") # returns 'None' or the value

    if type == None:

        fileName = request.args.getlist("file")[0]
        directory = request.args.getlist("device")[0]
        root = constants.LOG_DATA_LOCAL_LOCATION

        return send_from_directory(root + directory, fileName , as_attachment=True, attachment_filename=directory+ "_" + fileName.replace(".bin", ".binary") )
    else: 
        fileName = request.args.get("file")
        device = request.args.get("device")
        root = constants.CSV_LOG_DATA_LOCAL_LOCATION
 
        return send_from_directory(root + device, fileName , as_attachment=True, attachment_filename=device+ "_" + fileName )

@app.route('/downloadSeparated')
def downloadSeparated ():
    fileName = request.args.getlist("file")[0]
    device = request.args.getlist("device")[0]
    root = constants.LOG_DATA_LOCAL_LOCATION

   # theFile = log_to_split_csv_files(root + device + '/' + fileName, 'logdownload', device)
    theFiles = log_to_split_csv_files(root + device + '/' + fileName, 'log_csv_data/'+ device, device)

    fileList = ''
    for theFile in theFiles:
        fileList += theFile + "|"

    #return send_from_directory('logdownload', theFile , as_attachment=True, attachment_filename="separated_logs_" + device+ ".zip" )
    return redirect('view_log?devices[]=' + device + '&csv_ready=' + fileList + '&device=' + device)


def log_to_split_csv_files(logFile, outputDir, device):

    # actually first, make the output dir if not exists
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
        print("Log Directory Created for device: " + outputDir)


    # First delete all existing files
    for filename in os.listdir(outputDir):
        file_path = os.path.join(outputDir, filename)
        os.unlink(file_path)

    try:
        # Python 2
        xrange
    except NameError:
        # Python 3, xrange is now named range
        xrange = range

    with open(logFile, 'r') as log_file:

        splitLogs = {}
        log = log_file.read().splitlines()


        # Filip CSV rewrite added 26/03/2021

        for index,line in enumerate(log):
            line = json.loads(line)
            if "Timestamp" in line:
                # Cris timestamp fix 19/05/2021
                # It's a timestamp line, convert the timestamp
                timestamp = line["Timestamp"]["timestamp"]
                # Handle bad timestamps
                try:
                    # Cris timestamp fix 19/05/2021
                    # some timestamps are e.g. 21962, which get converted to 1970...
                    if timestamp > 1621000000:
                        timestamp = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d:%H-%M-%S")
                    else:
                        timestamp = 'invalid timestamp'
                except:
                    timestamp = 'invalid timestamp.'

                # Parse the next line underneath
                try:
                    logline = json.loads(log[index + 1])
                    logtype = list(logline.keys())[0]
                    if logtype not in splitLogs:
                        splitLogs[logtype] = []
                    logdetails = logline[logtype]
                    if logdetails == {}:
                        logdetails['unnamed'] = "-"
                    logdetails["time"] = timestamp
                    splitLogs[logtype].append(logdetails)
                except:
                    continue
            else:
                # No timestamp, skip
                continue

            ######  End Refactor 25/03/2021


        # CT 19/05/2021 - this was not working.  Different version added above.
        # Make output directory if doesn't exist
        # Path(outputDir).mkdir(parents=True, exist_ok=True)

        # Split logs, now turn them into a csv file each

        csvLibrary = []
        for category in splitLogs:
            f = open(outputDir + "/" + category + ".csv", "w")
            csv_file = csv.writer(f)

            # columns
            csv_file.writerow(list(splitLogs[category][0].keys()))

            # rows
            for item in splitLogs[category]:
                csv_file.writerow(item.values())

            csvLibrary.append(category + ".csv")


        # Cris remove Zipping as causing errors for some clients 19/05/2021
        # zipf = zipfile.ZipFile(outputDir + "/separated_logs_" + device + ".zip", "w", zipfile.ZIP_DEFLATED)

        # for root, dirs, files in os.walk(outputDir):
        #     for file in files:
        #         print(file)
        #         if file != "separated_logs_" + device + ".zip": # No zip inception 2 years later....

        #             zipf.write(os.path.join(root, file))

        # zipf.close()

        # Return name of zipfile
        #return "separated_logs_" + device + ".zip"

        #return the list of csv files created.
        return csvLibrary

@app.route('/download_file')
def downloadFile ():
    # this can be extended for other file types.
    # don't allow full file specificaiton

    allowedTypes = ['preset', 'script']

    fileName = request.args.getlist("file")[0]
    fileType = request.args.getlist("type")[0]


    if fileType in allowedTypes:
        if fileType == 'preset':
            fileLocation = "presets/" + fileName + '.json'
            downloadFileName = 'preset_'+fileName+'.json'
        if fileType == 'script':
            fileLocation = "scripts/" + fileName
            downloadFileName = 'script_'+fileName

        return send_from_directory('', fileLocation , as_attachment=True, attachment_filename=downloadFileName )

    # still here?  error.
    session['userMessage'] = {"type": 'error', "message": "Invalid file download request." }

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

    # the zip file = start with the date part of timezone / datetime
    dateTime = deviceFunctions.systemTime(constants.RUNMODE).split(' ', 1)[1]

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
    print("Seting clock to " + toTime + ' ' + passTo)
    deviceFunctions.syncHubToTime(constants.RUNMODE, toTime)

    # set user message
    session['userMessage'] = {"type": 'success', "message": "Hub clock updated to <strong>" + toTime + "</strong>"}

    return redirect(passTo)

@app.route('/my_actions')
def userActions():

    if 'userActions' in session:
        return json.dumps(session['userActions'])
    else:
        return 'None'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80) # for Developlent / Testing (Flask server)