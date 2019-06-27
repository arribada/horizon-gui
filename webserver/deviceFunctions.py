from flask import Flask
import subprocess
import json

debugMode = True # global


def callTrackerConfig(theCall):

    if  not debugMode:

        try:
            result = subprocess.check_output(["sudo", "tracker_config", theCall])

        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

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

