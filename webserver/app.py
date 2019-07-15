# Example file

from scute import scute
from flask import Flask, request
import json

## project functions
import deviceFunctions

app = Flask(__name__)

configFile = "testConfig"
config = __import__(configFile)

config.init()

options = {
        "reportSchema": "reportSchema.json",
        "actionsSchema": "actionsSchema.json",
        "configSchema": "configSchema.json",
        "dataViews": "dataViews.json",
    }

test = scute(options, app)

def getDevices():
    return ["1111111111111111", "2222222222222222", "333333333333", "666666666666666","444444444444", "5555555555555" ]

test.registerHook("get_devices", getDevices)

def getFields(deviceID):
    data =  deviceFunctions.getOneDeviceReport('dummy', deviceID)    
    #print(data)
    return(data)
    #return {"hello": "world"}

test.registerHook("get_report_fields", getFields)

# def getFriendlyName(deviceID):
#     return deviceID + "FRIENDLY"

# test.registerHook("get_report_field__friendlyName", getFriendlyName)

def saveConfig(deviceID, config):
    with open(deviceID + '_config.json', 'w') as configFile:  
        json.dump(config, configFile)

test.registerHook("save_config", saveConfig)

def readConfig(deviceID):
    with open(deviceID + '_config.json', 'r') as configFile:
        return json.load(configFile)

test.registerHook("read_config", readConfig)

@app.route('/export/<device>')
def export(device):
    return 'Export data for ' + device
    