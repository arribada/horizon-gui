from flask import Flask
from flask import jsonify
import subprocess
import json

import deviceFunctions

configFile = "testConfig"  # need to make this an env variable...
config = __import__(configFile)

runMode = config.runSettings['RUNMODE']

#  Welcome screen
def welcome():

    pageData = {
        "pageName": "Arribada Scan Results",
        "toolVersion": deviceFunctions.trackerConfigVesion(runMode),
        "data":  deviceFunctions.scanForAttachedDevices(runMode, config.runSettings['SCAN_USB'],config.runSettings['SCAN_BLUETOOTH'])
    } 
    pageData['numRows'] = len(pageData['data'])

    return pageData

def getTagStatus(tagID):

    pageData = {
        "pageName": "Tag Status",
        "toolVersion": deviceFunctions.trackerConfigVesion(runMode),
        "data":  deviceFunctions.getTagStatus(runMode, tagID)
    } 

    return pageData

def getTagConfig(tagID):

    pageData = {
        "pageName": "Tag Config",
        "toolVersion": deviceFunctions.trackerConfigVesion(runMode),
        "data":  deviceFunctions.getTagConfig(runMode, tagID)
    } 

    return pageData

