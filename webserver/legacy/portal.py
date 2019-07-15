from flask import Flask
from flask import render_template, request, redirect,\
    url_for, make_response, send_file, session, send_from_directory, jsonify
import json
import os
import os.path
import time
import os
import sys
from datetime import date, datetime, timedelta
import glob
import time
import re
import shutil
from functools import wraps
from shutil import copyfile
import subprocess
## project
import deviceFunctions




app = Flask(__name__)

noTagText = 'No Device Detected.' # this is in both files, so needs to be indluded...
scanUSB = True
scanBluetooth = False

# uploads test
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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
    batteryLevel = deviceFunctions.trackerConfigBattery()

    print(batteryLevel)

    return  "<div class='versionBlock'>Tool Version: " + toolVersion + " | " + batteryLevel + "</div>"




@app.route("/")
def hello():

    return welcome()

@app.route("/scan")
def scan():

    connected = {}

    # USB
    if scanUSB:
        connected['USB'] = deviceFunctions.scanForAttachedDevices('USB')
    print(connected)

    # Bluetooth
    if scanBluetooth:
        connected['Bluetooth'] = deviceFunctions.scanForAttachedDevices('Bluetooth')



    return jsonify(connected)



@app.route("/status")
def status():

    return htmlTrackerConfig("Status", "--status")   

@app.route("/version")
def version():

    return htmlTrackerConfig("Version", "--version") 


@app.route("/get_config")
def get_config():

    tracker_configResponse = deviceFunctions.getTrackerConfig()

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Get Config Results</h2>"

    if 'result' in tracker_configResponse:
        
        result += 'Loaded to ' + tracker_configResponse['result'] + '<br/><br/>'



        # read config file
        with open(tracker_configResponse['result'], 'r') as myConfig:
            data=myConfig.read()

        result += data + '<br/><br/>'

    else:
        result += tracker_configResponse['error']

    result += htmlInclude("htmlFooter")

    return result

@app.route("/erase_config")
def erase_config():

    return htmlTrackerConfig("Erase Config", "--erase_log") 




@app.route("/write_config")
def write_config():

    #tracker_configResponse = deviceFunctions.getTrackerConfig()

    
    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Write Config</h2>"

    # read config file
    with open('config/from_tag/current_config.json', 'r') as myConfig:
        data=myConfig.read()
    result += '<form action="/save_new_config" method="post">Update latest config read'
    result += '<textarea type="textarea" style="width:100%; height:400px; overflow-y: scroll" name="updateConfig">' + data  + '</textarea>'
    result += '<input type="submit" value="Save">'

    result += htmlInclude("htmlFooter")

    return result


@app.route("/save_new_config", methods = ['POST'])
def save_new_config():

   
    submittedConfig =  request.form["updateConfig"]


    newConfig =  open('config/to_tag/new_config.json', 'w')
    ## needs to be json, not string... TODO 
    newConfig.write(submittedConfig)
    newConfig.close()

    deviceFunctions.writeTrackerConfig()

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Save Config</h2>"



    result += htmlInclude("htmlFooter")

    return result



@app.route("/receive_logs")
def receive_logs():

    tracker_configResponse = deviceFunctions.receiveTrackerLogData()  # {'result': 'tracker_data/json/latest_json.json'}

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Receive Logs</h2>"

    data = ''

    if 'result' in tracker_configResponse:

        result += "Log Load time: %s" % time.ctime(os.path.getmtime(tracker_configResponse['result'])) + "<br><br>"

        # read log file
        with open(tracker_configResponse['result'], 'r') as myData:
            data=myData.read()


    result += data + '<br/><br/>'
    
    result += htmlInclude("htmlFooter")

    return result

@app.route("/download_logs")
def download_logs():

    # ensure there is a device connected...
    tracker_configResponse = deviceFunctions.callTrackerConfig('--status')

    print(tracker_configResponse)

    if tracker_configResponse != noTagText: 
        return send_file('tracker_data/json/latest_logfile.json', as_attachment=True)
    else:
        return



@app.route("/upload_file")
def upload_file():


    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Upload Test</h2>"

    result += '<form method=post enctype=multipart/form-data>'

    result += '<input type=file name=file><input type=submit value=Upload></form>'

    result += htmlInclude("htmlFooter")

    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)