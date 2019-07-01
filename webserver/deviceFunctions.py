from flask import Flask
import subprocess
import json

debugMode = False # global


def callTrackerConfig(theCall):

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", "tracker_config", theCall])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        print(result)
        
        result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result)

        if result.startswith('Unexpected error'):
            return {'error': 'No Devices detected'}
        else:
            result2 = json.loads(result)
            return {'result': result2}

    else:
        switcher = {
            '--status':{'result': {"cfg_version": 4, "ble_fw_version": 65704, "fw_version": 10, "debugMode": "On"} } 
        }
        return switcher.get(theCall, 'No Test data for ' + theCall)

def trackerConfigVesion():

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", "tracker_config", "--version"])

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

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", "tracker_config", "--battery"])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        result = result.rstrip() # trailing new line...
        result = json.loads(result)
        print(result['charging_level'])
        print("Raw tracker_config battery Received: " , result)
        resultString = 'Battery: ' + str(result['charging_level']) + '%'
       

    else: 
        resultString = "Battery: Debug Mode"


    return resultString


def getTrackerConfig():

    if  not debugMode:

        try:
            result = subprocess.check_output("sudo tracker_config --read config/from_tag/current_config.json",shell=True,stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data Received: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/from_tag/current_config.json'}
        else:
            return {'error': 'No Devices detected'}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}


def writeTrackerConfig():

    if  not debugMode:

        try:
            result = subprocess.check_output("sudo tracker_config --write config/to_tag/new_config.json",shell=True,stderr=subprocess.STDOUT)
            #also need to creat a log file...
            #sudo tracker_config --create_log LINEAR

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        
        #result = result.rstrip() # trailing new line...
        print("Raw tracker_config data saved: " , result, len(result))

        if len(result) == 0:
            return {'result': 'config/to_tag/new_config.json'}
        else:
            return {'error': 'No Devices detected'}
           

    else:

        return {'result': 'config/from_tag/current_config.json'}


