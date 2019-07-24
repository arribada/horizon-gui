from flask import Flask
import subprocess
import json
from scute import scute

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
       

        if scanBluetooth:
            # this will scan BT - might not be needed, but setting up...
            print("TODO - scanBluetooth")    
        
     
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


        result['batteryLevel'] = deviceBatteryLevel['result']['charging_level']
        result['firmwareVersion'] = deviceStatus['result']['fw_version']

        result['friendlyName'] = "Not Implemented"

        result['fileSize']  = deviceConfig['result']['logging.fileSize']
        result['fileType']  = deviceConfig['result']['logging.fileType']

        result['sensorsEnabled']  = []
        if deviceConfig['result']['accelerometer.logEnable']:
            result['sensorsEnabled'].append("Accelerometer")

        if deviceConfig['result']['gps.logPositionEnable']:
            result['sensorsEnabled'].append("GPS Position")

        if deviceConfig['result']['pressureSensor.logEnable']:
              result['sensorsEnabled'].append("Pressure")

        if deviceConfig['result']['saltwaterSwitch.logEnable']:
            result['sensorsEnabled'].append("Saltwater")

        if deviceConfig['result']['battery.logEnable']:
            result['sensorsEnabled'].append("Battery")
        
        if deviceConfig['result']['logging.dateTimeStampEnable']:
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
            data = horizonSCUTE.flattenJSON(json.load(configFile))

        return {'result': data}


def downloadDeviceConfigToLocal(deviceID):

        #??  deviceID.replace(":","")??
        configFileName = "config/from_tag/config" + deviceID.replace(":","") + ".json"

        try:
            result = subprocess.check_output("sudo " + constants.TRACKER_CONFIG + " --read " + configFileName + " --id " + deviceID  ,shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
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

        return "TODO"





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
           
