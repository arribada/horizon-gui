from flask import Flask
import subprocess
import json

import deviceFunctions

configFile = "testConfig"  # need to make this an env variable...
config = __import__(configFile)

#  Welcome screen
def welcome():

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Welcome</h2>"
    result += "<h3>Attached Tag</h3>"
    result += "<ul class='tag-functions'>"
    result += "<li><a href='/scan'>Scan For Tags</a><br/></li>"
    result += "<li><a href='/status'>Tag Status</a><br/></li>"
    result += "<li><a href='/get_config'>Read Tag Config</a><br/></li>"
    # result += "<li><a href='/erase_config'>Erase Tag Config</a><br/></li>"
    result += "<li><a href='/write_config'>Write Tag Config</a><br/></li>"
    result += "<li><a href='/receive_logs'>Receive Log Data</a><br/></li>"
    result += "<li><a href='/upload_file'>Test Upload</a><br/></li>"
    result += "<li><a href='/download_logs' target='_blank'>Download Log Data</a><br/></li>"

    result += "</ul>"
    result += trackerVersion()
    result += htmlInclude("htmlFooter")

    return result


#  display screen of result 
def htmlTrackerConfig(pageTitle, commandToRun):

    tracker_configResponse = deviceFunctions.callTrackerConfig(commandToRun)

    if type(tracker_configResponse) == "str":
        tracker_configResponse = json.load(tracker_configResponse)

    if "error" in tracker_configResponse:
        dataBlock = ''
        errorBlock = tracker_configResponse['error']
    else:
        errorBlock = ''
        dataBlock = tracker_configResponse['result']
 
    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>" + pageTitle + " Results</h2>"

    if len(errorBlock) != 0:
        result += "<span class='error'>No Devices detected.</span>"
    else:
        fieldColumns = dataBlock.keys()
        result += "<table>"
        result += "<tr>"

        for field in fieldColumns:
            result += "<th>" + field + "</th>"

        result += "</tr>"

        for field in fieldColumns:
            result += "<td>" + str(dataBlock[field]) + "</td>"

        result += "</tr>"


        result += "</table>"

    result += trackerVersion()
    result += htmlInclude("htmlFooter")

    return result


# standard Header
def htmlInclude(fileName):

    with open("includes/" + fileName + ".html", "r") as f1:
        dataRaw = f1.read()

    return dataRaw

def trackerVersion():

    toolVersion = deviceFunctions.trackerConfigVesion()
    #batteryLevel = deviceFunctions.trackerConfigBattery()


    return  "<div class='versionBlock'>Tool Version: " + toolVersion +  "</div>"


