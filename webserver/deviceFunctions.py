from flask import Flask, session
import subprocess
import json

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
            print("TODO - scanBluetooth")    
        
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
        deviceConfig = getDeviceConfig(runMode, deviceID)

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
                result['sensorsEnabled'].append("Accelerometer")

            if deviceConfig['result']['gps']['logPositionEnable']:
                result['sensorsEnabled'].append("GPS Position")

            if deviceConfig['result']['pressureSensor']['logEnable']:
                result['sensorsEnabled'].append("Pressure")

            if deviceConfig['result']['saltwaterSwitch']['logEnable']:
                result['sensorsEnabled'].append("Saltwater")

            if deviceConfig['result']['battery']['logEnable']:
                result['sensorsEnabled'].append("Battery")
            
            if deviceConfig['result']['logging']['dateTimeStampEnable']:
                result['sensorsEnabled'].append("Date Time")

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
        print("Raw tracker_config list_id Received: " , result)


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
        print("Raw tracker_config version Received: " , result)


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
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': constants.NO_TAG_TEXT}
        else:

            # the result is:  Connecting to device at index 0\n{"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10}
            # so we need to divide at the '\n' and json load the last part...
            result = result.split('\n')
            resultJson = json.loads(result[len(result) -1])
            return {'result': resultJson}


def getDeviceConfig(runMode, deviceID):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        configFile = "dummy_data/" + deviceID + ".json"
        
        with open(configFile) as json_file:  
            data = json.load(json_file)

        return data

    else:

        configFileName = downloadDeviceConfigToLocal(deviceID)

        if "error" in configFileName:
            return configFileName
        
        # read config file
        with open(configFileName['result'], 'r') as configFile:
            data = json.load(configFile)
        
        return {'result': data}


def downloadDeviceConfigToLocal(deviceID):

        #??  deviceID.replace(":","")??
        configFileName = constants.CONFIG_LOCAL_LOAD_LOCATION + "config-" + deviceID + ".json"


        try:
            result = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --read " + configFileName + " --id " + deviceID  ,shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        
        print("Raw tracker_config data Received: " , result, len(result))

        # result = 'Connecting to device at index 0\n'
        result = result.split('\n')
        resultResponse = result[len(result) -1]
        
        # some error...
        if len(resultResponse) != 0:
            return {'error': constants.NO_TAG_TEXT}

        return {'result': configFileName}



def saveDeviceConfig(runMode, deviceID, config):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        destinationFile = "dummy_data/" + deviceID + ".json"

        with open(destinationFile, 'w') as configFile:  
            json.dump(config, configFile)

        return "OK."

    else:

        if not constants.FRIENDLY_NAME_ACTIVE:
            del config["system"]["friendlyName"]

        configFileName = constants.CONFIG_LOCAL_SAVE_LOCATION + "config-" + deviceID + ".json"
        
        # convert to correct json types
        config = correctJsonTypesInConfig(config)



        with open(configFileName, 'w') as outfile:
            json.dump(config, outfile)
  
        try:
            result = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --write " + configFileName + " --id " + deviceID  ,shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        print("Raw tracker_config data saved: " , result, len(result))

        # result = 'Connecting to device at index 0\n'
        result = result.split('\n')
        resultResponse = result[len(result) -1]
        
        # some error...
        if len(resultResponse) != 0:
            return {'error': result[0]}

        return {'result': configFileName}


def correctJsonTypesInConfig(config):

    #print("in correctJsonTypesInConfig")
    #print(config)
    #print (config['saltwaterSwitch']['logEnable'])

    with open('configSchema.json') as json_file:
        masterSchema = json.load(json_file)

    #print(masterSchema)

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

                    if config[categoryName][splitFieldName[1]] == "on":

                        result[categoryName][splitFieldName[1]] = True 

                    elif config[categoryName][splitFieldName[1]] == "off":

                        result[categoryName][splitFieldName[1]] = False 
                    else:                                
                        # default?
                        if "default" in fieldData:
                            result[categoryName][splitFieldName[1]] = fieldData["default"]  

            else:
                # default value
                print(categoryName + " > " + splitFieldName[1] + " not in config")



    print(result)

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
        print("Raw tracker_config battery Received: " , result)



    if result.startswith('Unexpected error'):
        returnResult = {"error": constants.NO_TAG_TEXT}
        
    else:

        # the result is:  'Connecting to device at index 0\n{"charging_level": 100, "charging_ind": true}'
        # so we need to divide at the '\n' and json load the last part...
        result = result.split('\n')
        resultJson = json.loads(result[len(result) -1])
        returnResult  = {'result': resultJson}
       
    return returnResult



def receiveTrackerLogData(runMode, deviceID): 

    deviceID = deviceID.replace(":", "")

    
    if  runMode == 'dummy':

        destinationFile = "dummy_data/latest_logfile_" + deviceID + ".json"

        f = open(destinationFile, "r")

        fileContents = f.read()
        f.close()

        return {"file": destinationFile, "data": fileContents }

    else:
        # get data off the tag
        try:
            result1 = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --read_log tracker_data/binary/latest_binary.bin",shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        # convert to json
        try:
            result2 = subprocess.check_output("log_parse --file tracker_data/binary/latest_binary.bin > tracker_data/json/latest_logfile.json",shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        


        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config log data Received ")

        if len(result1) == 0 and len(result2) == 0:
            print("Raw tracker_config log data Received ")
            return {'result': 'tracker_data/json/latest_logfile.json'}
        else:
            return {'error': constants.NO_TAG_TEXT + ' or data error'}
           
