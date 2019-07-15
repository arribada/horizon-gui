from flask import Flask
import subprocess
import json

configFile = "testConfig"  # need to make this an env variable...
config = __import__(configFile)
tracker_configVersion = config.runSettings["TRACKER_CONFIG_VERSION"]

# load the dummy responses...
dummyResponseSet =config.runSettings["DUMMY_RESPONSE_MODULE"]
dummy = __import__(dummyResponseSet)
dummy.init()



def callTrackerConfig(theCall):

    if  config.runSettings['RUNMODE'] != 'dummy':

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

        return dummy.responses["SCAN"]

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
        

    


def trackerConfigVesion(runMode):

    if runMode == 'dummy':

        result = dummy.responses['VERSION']

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
        return dummy.responses['STATUS']

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


def getTagConfig(runMode, tagID):

    if  runMode == 'dummy':
        print(dummy.responses['CONFIG_FILE'])


        with open(dummy.responses['CONFIG_FILE']) as json_file:  
            data = json.load(json_file)

        return data

    else:

        return "TODO"






def trackerConfigBattery():

    if config.runSettings['RUNMODE'] != 'dummy':

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

    if  config.runSettings['RUNMODE'] != 'dummy':

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

    if  config.runSettings['RUNMODE'] != 'dummy':

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

    if  config.runSettings['RUNMODE'] != 'dummy':

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
