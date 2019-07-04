from flask import Flask
import subprocess
import json

debugMode = False # global
noTagText = 'No Device Detected.'  # this is in both files, so needs to be indluded...
tracker_configVersion = 'tracker_config'


def callTrackerConfig(theCall):

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, theCall])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        print(result)
        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': noTagText}
        else:
            result2 = json.loads(result)
            return {'result': result2}

    else:
        switcher = {
            '--status':{'result': {"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10, "debugMode": "On"} } 
        }
        return switcher.get(theCall, 'No Test data for ' + theCall)


def scanForAttachedDevices(connectionType):

    if not debugMode:
        
        result = {}

        # Poll each of the ports, if tag conneced, get it's --status and read it's config.  
        # Return list of: 
        #   portID
        #   deviceIdentifier
        #   frieldlyName (currently first 10 digits of deviceIdentifier)

        if connectionType == 'USB':
            # this will scan all.  just use the current connected for now.
            myDeviceConfigFile = getTrackerConfig()
            # read config file
            with open(myDeviceConfigFile['result'], 'r') as myConfig:
                data=myConfig.read()
            data =  json.load(data)
            
            print(data)
        

    else: 
        result = {"result": "Debug Mode"}


    return result


def trackerConfigVesion():

    if not debugMode:

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--version"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        result = result.rstrip() # trailing new line...
        print("Raw tracker_config version Received: " , result)

    else: 
        result = "Version: Debug Mode"

    if result.startswith('Unexpected error'):
        return 'Error - unexpected error.'
    else:
        return result

def trackerConfigBattery():

    if not debugMode:

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--battery"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config battery Received: " , result)

    else: 
        result = "Battery: Debug Mode"

    if result.startswith('Unexpected error'):
        result = noTagText
    else:
        result = result.rstrip() # trailing new line...
        result = json.loads(result)
        print(result['charging_level'])
        print("Raw tracker_config battery Received: " , result)
        result = 'Battery: ' + str(result['charging_level']) + '%'
       
    return result


def getTrackerConfig():

    if  not debugMode:

        try:
            result = subprocess.check_output("sudo " + tracker_configVersion + " --read config/from_tag/current_config.json",shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/from_tag/current_config.json'}
        else:
            return {'error': noTagText}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}



def writeTrackerConfig():

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", tracker_configVersion, "--write", "config/to_tag/new_config.json"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data saved: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/to_tag/new_config.json'}
        else:
            return {'error': noTagText}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}

def receiveTrackerLogData(): 

    if  not debugMode:

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
            return {'error': noTagText + ' or data error'}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}
