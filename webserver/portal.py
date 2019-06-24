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
def helloWorld():

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Welcome</h2>"
    result += "<h3>Attached Tag</h3>"
    result += "<ul class='tag-functions'>"
    result += "<li><a href='/version'>Version</a></li>"
    result += "<li><a href='/status'>Status</a></li>"
    result += "</ul>"
    result += htmlInclude("htmlFooter")

    return result


#  status Scan
def htmlTrackerConfig(htmlTitle, commandToRun):



    deviceList = deviceFunctions.callTrackerConfig(commandToRun)
    ## for testing without tracker_config
    #deviceList = [{"111":"a111", "222":"a222", "333":"a333", "444":"a444", }, {"111":"b111", "222":"b222", "333":"b333", "444":"b444", }]


    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>" + htmlTitle + " Results</h2>"

    if len(deviceList) == 0:
        result += "<span class='error'>No Devices detected.</span>"
    else:
        fieldColumns = deviceList[0].keys()
        result += "<table>"
        result += "<tr>"

        for field in fieldColumns:
            result += "<th>" + field + "</th>"

        result += "</tr>"

        for device in deviceList:
            result += "<tr>"
            for field in fieldColumns:
                result += "<td>" + str(device[field]) + "</td>"

            result += "</tr>"

        result += "</table>"

    result += htmlInclude("htmlFooter")

    return result



# standard Header
def htmlInclude(fileName):

    with open("includes/" + fileName + ".html", "r") as f1:
        dataRaw = f1.read()

    return dataRaw


@app.route("/")
def hello():

    return helloWorld()


@app.route("/status")
def status():

    return htmlTrackerConfig("Status", "--status")   

@app.route("/version")
def version():

    return htmlTrackerConfig("Version", "--version") 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)