from flask import Flask
import subprocess
import json


tracker_configVersion = "tracker_config"

# load the dummy responses...
with open('dummy_data/dummyResponses.json') as json_file:  
    dummyResponses = json.load(json_file)


def callTrackerConfig(theCall):

    if  runMode == 'dummy':

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, theCall])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        print(result)
        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': config.runSettings['NO_TAG_TEXT']}
        else:
            result2 = json.loads(result)
            return {'result': result2}

    else:
        switcher = {
            '--status':{'result': {"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10, "debugMode": "On"} } 
        }
        return switcher.get(theCall, 'No Test data for ' + theCall)


def scanForAttachedDevices(runMode, scanUSB, scanBluetooth):

    if runMode == 'dummy':
        return dummyResponses['SCAN'].keys()

    else: 
        
        result = {}

        # Poll each of the ports, if tag connected, get it's --status and read it's config.  

        if scanUSB:
            # this will scan all. 
            print("TODO - scanUSB") 


        if scanBluetooth:
            # this will scan all.
            print("TODO - scanBluetooth")    
        
        if not scanUSB and not scanBluetooth:
            #just use the current connected
            myDeviceConfigFile = getTrackerConfig()
            # read config file
            with open(myDeviceConfigFile['result'], 'r') as myConfig:
                data=myConfig.read()
            data =  json.load(data)
            
            print(data)
            # still TODO
        return "todo"
        

def getDeviceReport(runMode, deviceID):
    
    if runMode == 'dummy':
        return dummyResponses["SCAN"][deviceID]

    else: 
        
        result = {}

        # Poll each of the ports, if tag connected, get it's --status and read it's config.  

        return "todo"
        
    


def trackerConfigVesion(runMode):

    if runMode == 'dummy':

        result = dummyResponses['VERSION']

    else: 

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--version"])

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
            result = subprocess.check_output(["sudo", tracker_configVersion, '--status'])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        print(result)
        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': config.runSettings['NO_TAG_TEXT']}
        else:
            result2 = json.loads(result)
            return {'result': result2}


def getDeviceConfig(runMode, deviceID):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        configFile = "dummy_data/" + deviceID + ".json"
        print(configFile)
        
        with open(configFile) as json_file:  
            data = json.load(json_file)

        output = {}
        for categoryKey, categoryFields in data.items():
            for field, value in categoryFields.items():
                output[field] = value

        return output

    else:

        return "TODO"


def saveDeviceConfig(runMode, deviceID, config):

    if  runMode == 'dummy':

        deviceID = deviceID.replace(":", "")

        destinationFile = "dummy_data/" + deviceID + ".json"
        print(type(config))

        # load the configSchema for reference
        with open("configSchema.json") as json_file:  
            mainDictionary = json.load(json_file)
        #print(mainDictionary)

        output = {}

        for thisField, thisValue in config:
            print(thisField, thisValue)
            for categoryKey, categoryFields in mainDictionary.items():
                for field, value in categoryFields.items():
                    if field == thisField:
                        output[categoryKey][thisField] = thisValue
                
        print(output)


        # with open(destinationFile, 'w') as configFile:  
        #     json.dump(config, configFile)

        return "OK."

    else:

        return "TODO"





def trackerConfigBattery():

    if runMode == 'dummy':

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--battery"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config battery Received: " , result)

    else: 
        result = "Battery: Debug Mode"

    if result.startswith('Unexpected error'):
        result = config.runSettings['NO_TAG_TEXT']
    else:
        result = result.rstrip() # trailing new line...
        result = json.loads(result)
        print(result['charging_level'])
        print("Raw tracker_config battery Received: " , result)
        result = 'Battery: ' + str(result['charging_level']) + '%'
       
    return result


def getTrackerConfig():

    if  runMode == 'dummy':

        try:
            result = subprocess.check_output("sudo " + tracker_configVersion + " --read config/from_tag/current_config.json",shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/from_tag/current_config.json'}
        else:
            return {'error': config.runSettings['NO_TAG_TEXT']}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}



def writeTrackerConfig():

    if  runMode == 'dummy':

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--write", "config/to_tag/new_config.json"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data saved: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/to_tag/new_config.json'}
        else:
            return {'error': config.runSettings['NO_TAG_TEXT']}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}

def receiveTrackerLogData(): 

    if  runMode == 'dummy':

        # get data off the tag
        try:
            result1 = subprocess.check_output("sudo " + tracker_configVersion + " --read_log tracker_data/binary/latest_binary.bin",shell=True,stderr=subprocess.STDOUT)

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
            return {'error': config.runSettings['NO_TAG_TEXT'] + ' or data error'}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}
