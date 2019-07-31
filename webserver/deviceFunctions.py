from flask import Flask, session
import subprocess
import json
import os.path
import glob
import datetime

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

        # this returns {"0": "00:00:00:00:00:00:00:00"} for one, assume 
        # [ {"0": "00:00:00:00:00:00:00:00"},  {"1": "11:00:00:00:00:00:00:00"}]  for multiple

        if scanUSB:
            # this will scan all. 
            devices = deviceScan("USB")
            devices = json.loads(devices)

            for connectionID, deviceID in devices.items():
                result.append(deviceID)
                # add the device to session data..
                
       

        if scanBluetooth:
            # this will scan BT - might not be needed, but setting up...
            logMessage("TODO - scanBluetooth")    
        
        #result is a list of connected devices..
        #session['connectedDevices'] = result
     
        return result
        

def getDeviceReport(runMode, deviceID):
    
    if runMode == 'dummy':
        return dummyResponses["SCAN"][deviceID]

    else: 

        result = {}
        # battery level
        deviceBatteryLevel = getDeviceBattery(runMode, deviceID)

        # status items
        deviceStatus = getDeviceStatus(runMode, deviceID)

        # config items
        deviceConfig = getDeviceConfig(runMode, deviceID, True)

        if "result" in deviceBatteryLevel:
            result['batteryLevel'] = deviceBatteryLevel['result']['charging_level']


        if "result" in deviceStatus:
            result['firmwareVersion'] = deviceStatus['result']['fw_version']


        result['friendlyName'] = "Not Implemented"

        if "result" in deviceConfig:

            if constants.FRIENDLY_NAME_ACTIVE:
                result['friendlyName'] = deviceConfig['result']['system']['friendlyName']
            else:
                result['friendlyName'] = "Not Yet Implemented"

            
            result['fileSize']  = deviceConfig['result']['logging']['fileSize']
            result['fileType']  = deviceConfig['result']['logging']['fileType']
            

            result['sensorsEnabled']  = []
            if deviceConfig['result']['accelerometer']['logEnable']:
                result['sensorsEnabled'].append("Accelerometer.")

            if deviceConfig['result']['gps']['logPositionEnable']:
                result['sensorsEnabled'].append("GPS Position.")

            if deviceConfig['result']['pressureSensor']['logEnable']:
                result['sensorsEnabled'].append("Pressure.")

            if deviceConfig['result']['saltwaterSwitch']['logEnable']:
                result['sensorsEnabled'].append("Saltwater.")

            if deviceConfig['result']['battery']['logEnable']:
                result['sensorsEnabled'].append("Battery.")
            
            if deviceConfig['result']['logging']['dateTimeStampEnable']:
                result['sensorsEnabled'].append("Date Time.")

        return result
        
    


def deviceScan(runMode):

    if runMode == 'dummy':

        result = {"0": "00:00:00:00:00:00:00:00"}

    else: 

        try:
            result = subprocess.check_output(["sudo", constants.TRACKER_CONFIG, "--list_id"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        result = result.rstrip() # trailing new line...
        logMessage("Raw tracker_config list_id Received: " + result)


    if result.startswith('Unexpected error'):
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

    if  runMode == 'dummy':
        return dummyResponses['STATUS']

    else:

        try:
            testString = "sudo " + constants.TRACKER_CONFIG + " --status --id "+deviceID
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
        with open(configFileName, 'r') as configFile:
            data = json.load(configFile)
        
        return {'result': data}


def isConfigAlreadyOnLocal(deviceID):

    # if there is a directory in constants.CONFIG_LOCAL_LOAD_LOCATION for this device, get the latest file from it 
    if not os.path.exists(constants.CONFIG_LOCAL_LOAD_LOCATION + deviceID + '/' ):
        return False

    list_of_files = glob.glob(constants.CONFIG_LOCAL_LOAD_LOCATION + deviceID + '/*.' + constants.CONFIG_FILE_EXTENSION) 
    if not list_of_files: #no files
        return False

    latest_file = max(list_of_files, key=os.path.getctime)

    logMessage("Using Local config: "+ latest_file )
    return latest_file


def downloadDeviceConfigToLocal(deviceID):


        myConfigDirectory = constants.CONFIG_LOCAL_LOAD_LOCATION + deviceID + '/'

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
    # TODO
    #  loop myConfigDirectory = constants.CONFIG_LOCAL_LOAD_LOCATION + deviceID + '/'
    # and only keep the latest 10 files...
    print("TODO tidyUpConfigDirectory")


def saveDeviceConfig(runMode, deviceID, config):

    logMessage("device functions saveDeviceConfig")

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        destinationFile = "dummy_data/" + deviceID + ".json"

        with open(destinationFile, 'w') as configFile:  
            json.dump(config, configFile)

        return "OK."

    else:

        if not constants.FRIENDLY_NAME_ACTIVE:
            del config["system"]["friendlyName"]


        myConfigDirectory = constants.CONFIG_LOCAL_LOAD_LOCATION + deviceID + '/'

        if not os.path.exists(myConfigDirectory):
            os.mkdir(myConfigDirectory)

        currentDT = datetime.datetime.now()
        currentDateTime = currentDT.strftime("%Y%m%d_%H%M%S")

        newConfigFileName = myConfigDirectory + currentDateTime + "-" + deviceID + "." + constants.CONFIG_FILE_EXTENSION

        # convert to correct json types
        config = correctJsonTypesInConfig(config)

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
            # error coule mean malformed local config file for this device... remove it
            os.remove(configFileName)
            return {'error': result[0]}

        return {'result': configFileName}


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

            if splitFieldName[1] in config[categoryName]:

                if categoryName not in result:
                    result[categoryName] = {}

                # convert to correct jsonType
                if fieldData['jsonType'] == "number": 

                    if len(config[categoryName][splitFieldName[1]]) != 0:
                        result[categoryName][splitFieldName[1]] = float(config[categoryName][splitFieldName[1]])
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

                elif fieldData['jsonType'] == "int": 

                    if len(config[categoryName][splitFieldName[1]]) != 0:
                        result[categoryName][splitFieldName[1]] = int(config[categoryName][splitFieldName[1]])
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

                elif fieldData['jsonType'] == "text": 

                    if len(config[categoryName][splitFieldName[1]]) != 0:

                        result[categoryName][splitFieldName[1]] = config[categoryName][splitFieldName[1]]
                    else:
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

                elif fieldData['jsonType'] == "boolean": 
                   
                    if config[categoryName][splitFieldName[1]] == "selected":

                        result[categoryName][splitFieldName[1]] = True 

                    elif config[categoryName][splitFieldName[1]] == "notselected":

                        result[categoryName][splitFieldName[1]] = False 
                    else:                                
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

            else:
                logMessage(categoryName + " > " + splitFieldName[1] + " in configSchema.jason, but not in config sent")


    return result


def getDeviceBattery(runMode, deviceID):

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

    if  runMode == 'dummy':

        destinationFile = "dummy_data/latest_logfile_" + deviceID + ".json"

        f = open(destinationFile, "r")

        fileContents = f.read()
        f.close()

        return {"file": destinationFile, "data": fileContents }

    else:

        logPath = constants.LOG_DATA_LOCAL_LOCATION + deviceID 
        currentDT = datetime.datetime.now()
        currentDateTime = currentDT.strftime("%Y-%m-%d_%H:%M:%S")
        
        if not os.path.exists(logPath):
            os.makedirs(logPath)
            logMessage("Directory Created: " + logPath)

        binaryFile = logPath + "/" + currentDateTime + ".bin"
        jsonFile = logPath + "/" + currentDateTime + ".json"

        logMessage("Making call to get " + binaryFile )

        # get data off the tag
        try:
            result1 = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --read_log " + binaryFile + " --id " + deviceID ,shell=True,stderr=subprocess.STDOUT)
            logMessage("Call complete for " + binaryFile )

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


        result1 = result1.split('\n')
        
        logMessage("Raw tracker_config binary load result " )
        for row in result1:
            logMessage(row)

        result1Response = result1[len(result1) -1]

        # convert to json if success...
        if len(result1Response) == 0:
            try:
                logMessage("Making call to create " + jsonFile )
                result2 = subprocess.check_output("log_parse --file "+ binaryFile + " > " + jsonFile ,shell=True,stderr=subprocess.STDOUT)
                logMessage("Call complete for " + jsonFile )
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


            result2 = result2.split('\n')
            
            logMessage("Raw tracker_config json convert result " )
            for row in result2:
                logMessage(row)

            result2Response = result2[len(result2) -1]
        else:
            return {'error': constants.NO_TAG_TEXT + ' or data error'}


        if len(result1Response) == 0 and len(result2Response) == 0:
            logMessage("Raw tracker_config log data Received and converted")

            # write the dateTime to the lastLoaded file
            with open(logPath + "/latest_log.txt" , 'w+') as outfile:
                outfile.write(currentDateTime)

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
    logMessage("eraseLog for " + deviceID)

    if  runMode == 'dummy':
        return {'result': "erased"}
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

 
def flashDevice(runMode, deviceID): 
    logMessage("flashDevice for " + deviceID)

    if  runMode == 'dummy':
        return {'result': "flashed"}
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


def vewLatestLogData(runMode, deviceID, downloadNew):

    # force loading of new logs first...
    if downloadNew == "yes":
        receiveTrackerLogData(runMode, deviceID)

    # based on the latest loaded log (latest_log.txt), return:
    #  - log loaded data time
    #  - list of all logs
    #  - top 50 records of latest log
    #  - log inteligance: how many of what records in the json file...

    logPath = constants.LOG_DATA_LOCAL_LOCATION + deviceID

    latestLogInfo =open(logPath + "/latest_log.txt", "r")
    latestLogDate =latestLogInfo.read()

    logMessage("Getting info for " + logPath)

    logFiles = getLogFileListByDate(logPath, deviceID)

    logHead = getFileHead(logPath, latestLogDate + ".json", 50)

    logAnalysis = getLogAnalysis(logPath + "/" + latestLogDate + ".json")

    return {"selectedDevice":deviceID, "latestLogDateTime": latestLogDate.replace("_", " "), "logFilePath":logPath + "/", "fileHead": logHead, "allLogFiles": logFiles, "logAnalysis": logAnalysis }


def getLogFileListByDate(logPath, deviceID):

    if not os.path.exists(logPath):
        return "There are no logs for " + deviceID + ". Please request them."

    pathContent = os.listdir(logPath)

    tempDict = {}

    for file in pathContent:
        if file != "latest_log.txt":
            fileName = file.split(".")

            if fileName[0] not in tempDict:
                tempDict[fileName[0]] = {}
            tempDict[fileName[0]][fileName[1]] = file
    
    # converto to ordered list...
    returnFiles = []
    for key in reversed(sorted(tempDict.keys())):
        returnFiles.append({key: tempDict[key]})

    return returnFiles



def getFileHead(directory, fileName, count):
    
    if os.path.getsize(directory) > 0:
        # top 50 records
        with open(directory + '/' + fileName ) as myfile:
            head = [next(myfile) for x in xrange(50)]
        
        return json.dumps(head)
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
           
