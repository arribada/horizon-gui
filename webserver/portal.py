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


#  Welcome screen
def welcome():

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Welcome</h2>"
    result += "<h3>Attached Tag</h3>"
    result += "<ul class='tag-functions'>"
    result += "<li><a href='/status'>Tag Status</a></li>"
    result += "</ul>"
    result += trackerVersion()
    result += htmlInclude("htmlFooter")

    return result


#  status Scan
def htmlTrackerConfig(htmlTitle, commandToRun):

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

    result += "<h2>" + htmlTitle + " Results</h2>"

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

    return  "<div class='versionBlock'>track_config version: " + deviceFunctions.trackerConfigVesion() + "</div>"


@app.route("/")
def hello():

    return welcome()


@app.route("/status")
def status():

    return htmlTrackerConfig("Status", "--status")   

@app.route("/version")
def version():

    return htmlTrackerConfig("Version", "--version") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)