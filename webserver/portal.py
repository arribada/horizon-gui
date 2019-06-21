from flask import Flask
from flask import render_template, request, redirect,\
    url_for, make_response, send_file, session, send_from_directory, jsonify
import json
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
import deviceFunctions



app = Flask(__name__)

@app.route("/")
def hello():

    return helloWorld()


@app.route("/scan")
def scan():

    return scanForTags()    

if __name__ == "__main__":
    app.run()


#  Welcome screen
def helloWorld():

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Welcome</h2>"
    result += "<a href='/scan'>Scan For Tags</a>"

    result += htmlInclude("htmlFooter")

    return result


#  Welcome screen
def scanForTags():

    deviceList = deviceFunctions.listConnectedDevices()

    result = ''
    result += htmlInclude("htmlHeader")

    result += "<h2>Scan</h2>"

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