from flask import Flask, session
import subprocess
import json
import os.path
import glob
import datetime
from itertools import islice

# system config.
import constants


if constants.RUNMODE == "dummy":
    # load the dummy responses...
    with open(constants.DUMMY_RESPONSES) as json_file:  
        dummyResponses = json.load(json_file)


def scanForAttachedDevices(runMode, scanUSB, scanBluetooth):

    if runMode == 'dummy':
        return dummyResponses['SCAN'].keys()

    else: 
        
        result = []

        if scanUSB:
            # this will scan all. 
            devices = deviceScan("USB")
            #print(devices)

            if 'error' not in devices:
                devices = json.loads(devices)
                for connectionID, deviceID in devices.items():
                    result.append(deviceID)
                    # add the device to session data..
            else:
                result = devices    
       

        if scanBluetooth:
            # this will scan BT - might not be needed, but setting up...
            logMessage("TODO - scanBluetooth")    

        return result
        

def getDeviceReport(runMode, deviceID):

    deviceID = str(deviceID)     
    
    if runMode == 'dummy':
        return dummyResponses["SCAN"][deviceID]

    else: 

        result = {}
        #  all the details are now on --status
        
        # battery level
        #deviceBatteryLevel = getDeviceBattery(runMode, deviceID)
        # config items
        #deviceConfig = getDeviceConfig(runMode, deviceID, True)

        # status items - this now has all the report items
        deviceStatus = getDeviceStatus(runMode, deviceID)

        if "result" in deviceStatus:
            
            if deviceStatus['result']['charge_level'] == 254:
                result['batteryLevel'] = "<a class='noUnderline' href='#' title='" + constants.BATTERY_ERROR_TOOLTIP + "'>" + constants.BATTERY_ERROR_TEXT +  "</a>"
            else:
                result['batteryLevel'] = str(deviceStatus['result']['charge_level'] ) + "%"
            
            result['firmwareVersion'] = deviceStatus['result']['fw_version']

            result['hardwareID'] = deviceID

            result['friendlyName'] = setFriendlyName(deviceID)

            result['fileSize']  = deviceStatus['result']['log_file_size']

            result['sensorsEnabled']  = []
            if deviceStatus['result']['accel_enabled']:
                result['sensorsEnabled'].append("Accelerometer: ON")
            else:
                result['sensorsEnabled'].append("Accelerometer: Off")

            if deviceStatus['result']['pressure_enabled']:
                result['sensorsEnabled'].append("Pressure: ON")
            else:
                result['sensorsEnabled'].append("Pressure: Off")

            if deviceStatus['result']['temp_enabled']:
                result['sensorsEnabled'].append("Temp: ON")
            else:
                result['sensorsEnabled'].append("Temp: Off")


            # these were in the old config, but not in current --status
            # if deviceStatus['result']['gps']['logPositionEnable']:
            #     result['sensorsEnabled'].append("GPS Position.")

            # if deviceStatus['result']['saltwaterSwitch']['logEnable']:
            #     result['sensorsEnabled'].append("Saltwater.")

            # if deviceStatus['result']['battery']['logEnable']:
            #     result['sensorsEnabled'].append("Battery.")
            
            # if deviceStatus['result']['logging']['dateTimeStampEnable']:
            #     result['sensorsEnabled'].append("Date Time.")

        return result
        
    


def deviceScan(runMode):

    if runMode == 'dummy':

        result = {"0": "1234567890123456789"}

    else: 

        try:
            result = subprocess.check_output(["sudo", constants.TRACKER_CONFIG, "--list_id"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        result = result.rstrip() # trailing new line...
        
        logMessage("Raw tracker_config list_id Received: " + result)

    # device with incompatible firmware breaks the call.
    if 'requires a buffer of at least 31 bytes' in result:
        return {'error':'Incompatible Device Detected','message': 'One or more connected devices do not dontain the correct firmware.  Please check device. You can use the Scripts Menu to update firmware.'}
    elif result.startswith('Unexpected error'):
        return "{}" # no devices...
    else:
        return result



def trackerConfigVesion(runMode):

    if runMode == 'dummy':

        result = dummyResponses['VERSION']

    else: 

        try:
            result = subprocess.check_output(["sudo", constants.TRACKER_CONFIG, "--version"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        result = result.rstrip() # trailing new line...
        logMessage("Raw tracker_config version Received: " + result)


    if result.startswith('Unexpected error'):
        return 'Error - unexpected error.'
    else:
        return result


def getDeviceStatus(runMode, deviceID):

    deviceID = str(deviceID) 

    testString = "sudo " + constants.TRACKER_CONFIG + " --status --id " + deviceID

    if  runMode == 'dummy':
        return dummyResponses['STATUS']

    else:

        try:
            
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        
        result = result.rstrip() # trailing new line...


        if result.startswith('Unexpected error'):
            logMessage(result)
            return {'error': constants.NO_TAG_TEXT}
        else:

            # the result is:  Connecting to device at index 0\n{"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10}
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')

            logMessage("Raw tracker_config status result" )
            for row in result:
                logMessage(row)

            resultJson = json.loads(result[len(result) -1])
            return {'result': resultJson}


def getDeviceConfig(runMode, deviceID, forceReload = False):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        configFile = "dummy_data/" + deviceID + ".json"
        
        with open(configFile) as json_file:  
            data = json.load(json_file)

        return data

    else:
        
        if forceReload:
            configFileName = downloadDeviceConfigToLocal(deviceID)['result']
        else:
            # if there is already a file loaded, don't load it again...
            configFileName = isConfigAlreadyOnLocal(deviceID)
            if not configFileName:
                configFileName = downloadDeviceConfigToLocal(deviceID)['result']
          

        if "error" in configFileName:
            return configFileName
        
        # read config file
        print("getDeviceConfig " + configFileName)

        with open(configFileName, 'r') as configFile:
            data = json.load(configFile)

        return {'result': data}


def isConfigAlreadyOnLocal(deviceID):

    deviceID = str(deviceID) 

    # if there is a directory in constants.CONFIG_DATA_LOCAL_LOCATION for this device, get the latest file from it 
    if not os.path.exists(constants.CONFIG_DATA_LOCAL_LOCATION + deviceID + '/' ):
        return False

    list_of_files = glob.glob(constants.CONFIG_DATA_LOCAL_LOCATION + deviceID + '/*.' + constants.CONFIG_FILE_EXTENSION) 
    if not list_of_files: #no files
        return False

    latest_file = max(list_of_files, key=os.path.getctime)

    logMessage("Using Local config: "+ latest_file )

    # only keep constants.CONFIG_FILE_NUMBER_TO_KEEP different files
    tidyUpConfigDirectory(deviceID)

    return latest_file


def downloadDeviceConfigToLocal(deviceID):

        deviceID = str(deviceID) 

        myConfigDirectory = constants.CONFIG_DATA_LOCAL_LOCATION + deviceID + '/'

        if not os.path.exists(myConfigDirectory):

            os.mkdir(myConfigDirectory)

        currentDT = datetime.datetime.now()
        currentDateTime = currentDT.strftime("%Y%m%d_%H%M%S")

        newConfigFileName = myConfigDirectory + currentDateTime + "-" + deviceID + "." + constants.CONFIG_FILE_EXTENSION

        try:
            result = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --read " + newConfigFileName + " --id " + deviceID  ,shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        # result = 'Connecting to device at index 0\n'
        result = result.split('\n')

        logMessage("Raw tracker_config config load recieved" )
        for row in result:
            logMessage(row)
            
        resultResponse = result[len(result) -1]
        
        # some error...
        if len(resultResponse) != 0:
            return {'error': constants.NO_TAG_TEXT}

        # only keep constants.CONFIG_FILE_NUMBER_TO_KEEP different files
        tidyUpConfigDirectory(deviceID)

        return {'result': newConfigFileName}


def tidyUpConfigDirectory(deviceID):

    deviceID = str(deviceID)

    root = constants.CONFIG_DATA_LOCAL_LOCATION

    fileList = os.listdir(root + deviceID)
    fileList.sort(reverse=True)

    for i in range (len(fileList)): 
        if i >= constants.CONFIG_FILE_NUMBER_TO_KEEP: 
            # delete older files..
            os.remove(root + deviceID + "/" +  fileList[i])
        




def saveDeviceConfig(runMode, deviceID, config):

    logMessage("device functions saveDeviceConfig")

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        destinationFile = "dummy_data/" + deviceID + ".json"

        with open(destinationFile, 'w') as configFile:  
            json.dump(config, configFile)

        return "OK."

    else:

        # set the friendly name if sent, then remove the 'local' settings
        if 'local' in config:
            if 'friendlyName' in config["local"]:
                
                saveFriendlyName(deviceID, config["local"]['friendlyName'])

            del config["local"]

        
        #print(config)
 
        myConfigDirectory = constants.CONFIG_DATA_LOCAL_LOCATION + deviceID + '/'
        if not os.path.exists(myConfigDirectory):
            os.mkdir(myConfigDirectory)
        currentDT = datetime.datetime.now()
        currentDateTime = currentDT.strftime("%Y%m%d_%H%M%S")
        newConfigFileName = myConfigDirectory + currentDateTime + "-" + deviceID + "." + constants.CONFIG_FILE_EXTENSION
        # convert to correct json types
        config = correctJsonTypesInConfig(config)
        #print(config)

        # save this config locally
        with open(newConfigFileName, 'w+') as outfile:
            json.dump(config, outfile)

        try:
            result = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --write " + newConfigFileName + " --id " + deviceID  ,shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        

        # result = 'Connecting to device at index 0\n'
        result = result.split('\n')
        
        logMessage("Raw tracker_config data save result " )
        for row in result:
            logMessage(row)

        resultResponse = result[len(result) -1]

        
        # some error...
        if len(resultResponse) != 0:
            # error could mean malformed local config file for this device... remove it
            os.remove(newConfigFileName)
            return {'error': result[0]}

        # for field test the system.deviceIdentifier is editable and is the deviceID
        # flag back to calling routine if this has changed..

        return {'result': newConfigFileName}



def correctJsonTypesInConfig(config):

    with open('configSchema.json') as json_file:
        masterSchema = json.load(json_file)

    result = {}

    for categoryName, categoryData in masterSchema.items(): 

        if "hasSubLevel" in categoryData:
            #  skip for now - will need to cone back to this.  See gps.lastKnownPosition in config.
            continue
        
        for fieldName, fieldData in categoryData['fields'].items():
            
            
            splitFieldName = fieldName.split(".")

            # ignore data in the 'local' block
            if splitFieldName[0] == 'local':
                continue

            elif splitFieldName[1] in config[categoryName]:

                if categoryName not in result:
                    result[categoryName] = {}


                if 'jsonType' not in fieldData or fieldData['jsonType'] == "text":
                    if len(config[categoryName][splitFieldName[1]]) != 0:

                        result[categoryName][splitFieldName[1]] = config[categoryName][splitFieldName[1]]
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]                     

                elif fieldData['jsonType'] == "number": 

                    if len(config[categoryName][splitFieldName[1]]) != 0:
                        result[categoryName][splitFieldName[1]] = float(config[categoryName][splitFieldName[1]])
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

                elif fieldData['jsonType'] == "int": 

                    if config[categoryName][splitFieldName[1]] != '':
                        result[categoryName][splitFieldName[1]] = int(config[categoryName][splitFieldName[1]])
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  


                elif fieldData['jsonType'] == "boolean": 

                    if config[categoryName][splitFieldName[1]] == True:

                        result[categoryName][splitFieldName[1]] = True 

                    elif config[categoryName][splitFieldName[1]] == False:

                        result[categoryName][splitFieldName[1]] = False 
                    else:                                
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

            else:
                logMessage(categoryName + " > " + splitFieldName[1] + " in configSchema.json, but not in config sent")


    return result


def getDeviceBattery(runMode, deviceID):

    deviceID = str(deviceID) 

    if runMode == 'dummy':

        return {"result": "-"}

    else:

        try:

            testString = "sudo " + constants.TRACKER_CONFIG + " --battery --id "+deviceID
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        result = result.rstrip() # trailing new line...

    if result.startswith('Unexpected error'):
        returnResult = {"error": constants.NO_TAG_TEXT}
        
    else:

        # the result is:  'Connecting to device at index 0\n{"charging_level": 100, "charging_ind": true}'
        # so we need to divide at the '\n' and json load the last part...
        result = result.split('\n')

        logMessage("Raw tracker_config battery result " )
        for row in result:
            logMessage(row)


        resultJson = json.loads(result[len(result) -1])
        returnResult  = {'result': resultJson}
       
    return returnResult



def receiveTrackerLogData(runMode, deviceID):

    deviceID = str(deviceID)

    if runMode == 'dummy':

        destinationFile = "dummy_data/latest_logfile_" + deviceID + ".json"

        f = open(destinationFile, "r")

        fileContents = f.read()
        f.close()

        return {"file": destinationFile, "data": fileContents}

    else:

        logPath = constants.LOG_DATA_LOCAL_LOCATION + deviceID
        currentDT = datetime.datetime.now()
        currentDateTime = currentDT.strftime("%Y-%m-%d_%H:%M:%S")
        print("receiveTrackerLogData logPath=" + logPath)

        if not os.path.exists(logPath):
            os.makedirs(logPath)
            logMessage("Directory Created: " + logPath)

        binaryFile = logPath + "/" + currentDateTime + ".bin"
        jsonFile = logPath + "/" + currentDateTime + ".json"

        logMessage("Making call to get " + binaryFile)

        # get data off the tag
        try:
            result1 = subprocess.check_output(
                "sudo " + constants.TRACKER_CONFIG + " --read_log " +
                binaryFile + " --id " + deviceID,
                shell=True,
                stderr=subprocess.STDOUT)
            logMessage("Call complete for " + binaryFile)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "command '{}' return with error (code {}): {}".format(
                    e.cmd, e.returncode, e.output))

        result1 = result1.split('\n')

        logMessage("Raw tracker_config binary load result ")
        for row in result1:
            logMessage(row)

        result1Response = result1[len(result1) - 1]

        # convert to json if success...
        if len(result1Response) == 0:
            try:
                logMessage("Making call to create " + jsonFile)
                result2 = subprocess.check_output(
                    "log_parse --file " + binaryFile + " > " + jsonFile,
                    shell=True,
                    stderr=subprocess.STDOUT)
                logMessage("Call complete for " + jsonFile)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(
                    "command '{}' return with error (code {}): {}".format(
                        e.cmd, e.returncode, e.output))

            result2 = result2.split('\n')

            logMessage("Raw tracker_config json convert result ")
            for row in result2:
                logMessage(row)

            result2Response = result2[len(result2) - 1]
        else:
            return {'error': constants.NO_TAG_TEXT + ' or data error'}

        if len(result1Response) == 0 and len(result2Response) == 0:
            logMessage("Raw tracker_config log data Received and converted")

            return {'result': 'currentDateTime'}
        else:
            return {'error': constants.NO_TAG_TEXT + ' or data error'}


def writeGPSAlmanacToDevice(runMode, deviceID, fileToApply):

    if runMode == 'dummy':

        return {"result": "-"}

    else:

        try:

            testString = "sudo " + constants.TRACKER_CONFIG + " sudo gps_almanac --file upload/gps_almanac" + fileToApply + " --id "+deviceID
            print("Sending: " + testString)
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        result = result.rstrip() # trailing new line...

    if result.startswith('Unexpected error'):
        returnResult = {"error": constants.NO_TAG_TEXT}
        
    else:

        # the result is:  'Connecting to device at index 0\n{"charging_level": 100, "charging_ind": true}'
        # so we need to divide at the '\n' and json load the last part...
        result = result.split('\n')

        logMessage("Raw tracker_config upload Almanac result " )
        for row in result:
            logMessage(row)


        resultJson = json.loads(result[len(result) -1])
        returnResult  = {'result': resultJson}
       
    return returnResult






def dummyResponse(runMode, deviceID, runtype): 

    message = runtype + "for " + deviceID + " not yet implemented"
    logMessage(message)
    return message


def eraseLog(runMode, deviceID): 

    deviceID = str(deviceID) 

    logMessage("eraseLog for " + deviceID)

    if  runMode == 'dummy':
        return {"type": "success",  "message": "Log Erased for " + deviceID}
    else:

        try:
            testString = "sudo " + constants.TRACKER_CONFIG + " --erase_log --id "+deviceID
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        
        result = result.rstrip() # trailing new line...


        if result.startswith('Unexpected error'):
            logMessage(result)
            return {'error': constants.NO_TAG_TEXT}
        elif "CMD_ERROR_FILE_NOT_FOUND" in result:
            return {"result":"No Log file to erase."}
        else:

            # the result is:  Connecting to device at index 0\n{"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10}
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')

            logMessage("Raw tracker_config status result" )
            for row in result:
                logMessage(row)

            if len(result) == 1:
                return {'result': "erased"}
            else:
                return {'result': "Noterased"}


def createLog(runMode, deviceID): 

    deviceID = str(deviceID) 

    logMessage("createLog for " + deviceID)

    if  runMode == 'dummy':
        return {"type": "success",  "message": "Log Created for " + deviceID}
    else:

        try:
            testString = "sudo " + constants.TRACKER_CONFIG + " --create_log LINEAR --id "+deviceID
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        
        result = result.rstrip() # trailing new line...


        if result.startswith('Unexpected error'):
            logMessage(result)
            return {'error': constants.NO_TAG_TEXT}
        else:

            # the result is:  Connecting to device at index 0\n{"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10}
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')

            logMessage("Raw tracker_config create log result" )
            for row in result:
                logMessage(row)

            if len(result) == 1:
                return {'result': "created"}
            else:
                return {'result': "Notcreated"}
 
def flashDevice(runMode, deviceID): 

    deviceID = str(deviceID) 

    logMessage("flashDevice for " + deviceID)

    if  runMode == 'dummy':
        return {"type": "success",  "message": "Device Flashed: " + deviceID}
    else:

        try:
            testString = "sudo " + constants.TRACKER_CONFIG + " --reset FLASH --id "+deviceID
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        
        result = result.rstrip() # trailing new line...
        print(result)

        if result.startswith('Unexpected error'):
            logMessage(result)
            return {'error': constants.NO_TAG_TEXT}
        # elif "CMD_ERROR_FILE_NOT_FOUND" in result:
        #     return {"result":"No Log file to erase."}
        else:

            # the result is:  Connecting to device at index 0\n{"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10}
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')

            logMessage("Raw tracker_config status result" )
            for row in result:
                logMessage(row)

            if len(result) == 1:
                return {'result': "flashed"}
            else:
                return {'result': "NotFlashed"}

def eraseDevice(runMode, deviceID): 

    deviceID = str(deviceID) 

    logMessage("eraseDevice for " + deviceID)

    if  runMode == 'dummy':
        return {"type": "success",  "message": "Device Erased: " + deviceID}
    else:

        try:
            testString = "sudo " + constants.TRACKER_CONFIG + " --erase --id "+deviceID
            result = subprocess.check_output(testString,shell=True,stderr=subprocess.STDOUT) # these last parts are needed if you don't send an array

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        
        result = result.rstrip() # trailing new line...
        print(result)

        if result.startswith('Unexpected error'):
            logMessage(result)
            return {'error': constants.NO_TAG_TEXT}
        else:
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')

            logMessage("Raw tracker_config status result" )
            for row in result:
                logMessage(row)

            if len(result) == 1:
                return {'result': "erased"}
            else:
                return {'result': "NotErased"}






def viewLatestLogData(runMode, deviceID, downloadNew):

    # force loading of new logs first...
    if downloadNew == "yes":
        receiveTrackerLogData(runMode, deviceID)

    # based on the latest loaded log (latest_log.txt), return:
    #  - log loaded data time
    #  - list of all logs
    #  - top 50 records of latest log
    #  - log inteligance: how many of what records in the json file...

    logPath = constants.LOG_DATA_LOCAL_LOCATION + deviceID

    # log might not exist...
    try:
        latestLogInfo =open(logPath + "/latest_log.txt", "r")
    except:
        return {"selectedDevice":deviceID, "latestLogDateTime": '', "logFilePath":logPath + "/", "fileHead": [], "allLogFiles": [], "logAnalysis": [] }

    # this file holds the date time of the last log read time
    latestLogDate =latestLogInfo.read()

    logMessage("Getting info for " + logPath)

    # all the log files available
    logFiles = getLogFileListByDate(logPath, deviceID)

    # top 50 records of the file
    logHead = getFileHead(logPath, latestLogDate + ".json", 50)

    # analysis of the log file records
    logAnalysis = getLogAnalysis(logPath + "/" + latestLogDate + ".json")

    return {"selectedDevice":deviceID, "latestLogDateTime": latestLogDate.replace("_", " "), "logFilePath":logPath + "/", "fileHead": logHead, "allLogFiles": logFiles, "logAnalysis": logAnalysis }


def getLogFileListByDate(logPath, deviceID):

    deviceID = str(deviceID)

    if not os.path.exists(logPath):
        return "There are no logs for " + deviceID + ". Please request them."

    pathContent = os.listdir(logPath)

    tempDict = {}

    for file in pathContent:
        if file != "latest_log.txt":

            fileName = file.split(".")

            # add new download dates to output
            if fileName[0] not in tempDict:
                tempDict[fileName[0]] = {}

            thisFileSize = os.path.getsize(logPath + '/'+ file)
            if thisFileSize != 0:
                if thisFileSize < 1000:
                    thisFileSize = str(thisFileSize) + ' bytes'
                else:

                    thisFileSize = int(thisFileSize /1000)

                    if thisFileSize > 1000:
                        thisFileSize = str(int(thisFileSize /1000)) + ' Mb'

                    else:
                        thisFileSize = str(thisFileSize) + ' Kb'
            else: 
                thisFileSize = '0Kb'
                
            thisFile = {'fileName': file, 'fileSize': thisFileSize}

            tempDict[fileName[0]][fileName[1]] = thisFile

    # converto to ordered list...
    returnFiles = []
    for key in reversed(sorted(tempDict.keys())):
        returnFiles.append({key: tempDict[key]})

    return returnFiles



def getFileHead(directory, fileName, count):
    
    if os.path.getsize(directory) > 0:
        # top 50 records
        with open(directory + '/' + fileName ) as myfile:
            head = list(islice(myfile, count))
        
        return head
    else:

        return "No Log Data"
    
    return 



def getLogAnalysis(logFileName):

    logMessage(logFileName)

    outputTypes = []
    resultsDict = {}

    with open(logFileName, "r") as file:
        for line in file.readlines():
            thisLine = json.loads(line.rstrip()) #convert to json
            
            for key in thisLine:  # check to see if this type already in the output results
                if key not in outputTypes:
                    outputTypes.append(key)
                    resultsDict[key] = {"name": key, "first": thisLine[key], "last": "", "count": 1}
                else:
                    resultsDict[key]["count"] += 1
                    resultsDict[key]["last"] = thisLine[key]


    #print(resultsDict)
    outputResults = []
    for row in resultsDict:
        outputResults.append(resultsDict[row])

    return outputResults


def logMessage(message):
    # expand on this later.
    if constants.LOGGING_LEVEL == "verbose":
        print(message)


def setFriendlyName(deviceID):
    # if the device is already known, get its friendly name, otherwise write it to the file,
    # using the deviceID
    existingDevices = readKnownDevivces()
    #print(existingDevices)

    if deviceID in existingDevices:
        return existingDevices[deviceID]['friendlyName']
    else:
        # set friendly name to device id
        saveFriendlyName(deviceID, deviceID)
        return deviceID


def getFriendlyName(deviceID):

    existingDevices = readKnownDevivces()

    if deviceID in existingDevices:
        return existingDevices[deviceID]['friendlyName']
    else:
        return "Not Set"


def saveFriendlyName(deviceID, friendlyName):

    existingDevices = readKnownDevivces()

    if deviceID in existingDevices:
          existingDevices[deviceID]['friendlyName'] = friendlyName
    else:
        existingDevices[deviceID] = {'friendlyName': friendlyName}
        
    with open('knownDevices.json', 'w') as outfile:
        json.dump(existingDevices, outfile)

    return


def readKnownDevivces():

    try:
        with open('knownDevices.json') as json_file:
            data = json.load(json_file)
    except: 
        print ('Error reading /knownDevices.json')

    return data
           
