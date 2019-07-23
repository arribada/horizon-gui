from flask import Flask
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
                print(connectionID, deviceID)
                result.append(deviceID)


         

        if scanBluetooth:
            # this will scan BT - might not be needed, but setting up...
            print("TODO - scanBluetooth")    
        
        # if not scanUSB and not scanBluetooth: # this is not needed, but keep for a bit.
        #     #just use the current connected
        #     myDeviceConfigFile = getTrackerConfig()
        #     # read config file
        #     with open(myDeviceConfigFile['result'], 'r') as myConfig:
        #         data=myConfig.read()
        #     data =  json.load(data)
            
        #     print(data)
        #     # still TODO
        print(result)
        return result
        

def getDeviceReport(runMode, deviceID):
    
    if runMode == 'dummy':
        return dummyResponses["SCAN"][deviceID]

    else: 
        print("getDeviceReport", deviceID)

        result = {}
        
        batteryLevel = trackerConfigBattery(runMode, deviceID)

        result['batteryLevel'] = batteryLevel
        result['friendlyName'] = "Not Real"



        #    "id": "11:11:00:00:00:00",
        #    "batteryLevel": 50,
        #    "fileSize": 123456,
        #    "sensorsEnabled": [
        #        "gps",
        #        "pressure",
        #        "saltwater",
        #        "accelerometer"
        #    ],
        #    "firmwareVersion": 4,
        #    "fileType": "LINEAR"



        print (result)

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


def getTagStatus(runMode, tagID):

    if  runMode == 'dummy':
        return dummyResponses['STATUS']

    else:

        try:
            result = subprocess.check_output(["sudo", constants.TRACKER_CONFIG, '--status'])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        print(result)
        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': constants.NO_TAG_TEXT}
        else:
            result2 = json.loads(result)
            return {'result': result2}


def getDeviceConfig(runMode, deviceID):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        configFile = "dummy_data/" + deviceID + ".json"
        
        with open(configFile) as json_file:  
            data = json.load(json_file)

        # output = {}
        # for categoryKey, categoryFields in data.items():
        #     for field, value in categoryFields.items():
        #         output[field] = value

        return data

    else:

        return "TODO"


def saveDeviceConfig(runMode, deviceID, config):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        destinationFile = "dummy_data/" + deviceID + ".json"

        with open(destinationFile, 'w') as configFile:  
            json.dump(config, configFile)

        return "OK."

    else:

        return "TODO"





def trackerConfigBattery(runMode, deviceID):

    if runMode == 'dummy':

        return "-"

    else:

        try:
            result = subprocess.check_output(["sudo", constants.TRACKER_CONFIG, "--battery"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config battery Received: " , result)



    if result.startswith('Unexpected error'):
        result = constants.NO_TAG_TEXT
    else:
        result = result.rstrip() # trailing new line...
        result = json.loads(result)

        result = str(result['charging_level'])
       
    return result



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
           
