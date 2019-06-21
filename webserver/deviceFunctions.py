from flask import Flask
import subprocess





def listConnectedDevices():

    result = []

    result = subprocess.check_output("sudo tracker_config --status")

    result.append({"ID": "123/432", "value2": 23, "value3":15})
    result.append({"ID": "123/444", "value2": 18, "value3":88})

    return result