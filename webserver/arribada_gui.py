#!/usr/bin/env python
from flask import Flask
from flask import render_template, request, redirect,\
    url_for, make_response, send_file, session, send_from_directory, jsonify
import json
import os
import time
import sys
import glob

import subprocess

app = Flask(__name__)

configFile = "testConfig"
config = __import__(configFile)

config.init()

## project functions
import deviceFunctions
import routingFunctions

@app.route("/")
def hello():

    return routingFunctions.welcome()



@app.route("/status/<tagID>")
def status(tagID):

    return routingFunctions.getTagStatus(tagID)   


@app.route("/config/get/<tagID>")
def getconfig(tagID):

    return routingFunctions.getTagConfig(tagID)   




@app.route("/get_config")
def get_config():

    tracker_configResponse = deviceFunctions.getTrackerConfig()

    result = ''
    result += routingFunctions.htmlInclude("htmlHeader")

    result += "<h2>Get Config Results</h2>"

    if 'result' in tracker_configResponse:
        
        result += 'Loaded to ' + tracker_configResponse['result'] + '<br/><br/>'



        # read config file
        with open(tracker_configResponse['result'], 'r') as myConfig:
            data=myConfig.read()

        result += data + '<br/><br/>'

    else:
        result += tracker_configResponse['error']

    result += routingFunctions.htmlInclude("htmlFooter")

    return result

@app.route("/erase_config")
def erase_config():

    return routingFunctions.htmlTrackerConfig("Erase Config", "--erase_log") 




@app.route("/write_config")
def write_config():

    #tracker_configResponse = deviceFunctions.getTrackerConfig()

    
    result = ''
    result += routingFunctions.htmlInclude("htmlHeader")

    result += "<h2>Write Config</h2>"

    # read config file
    with open('config/from_tag/current_config.json', 'r') as myConfig:
        data=myConfig.read()
    result += '<form action="/save_new_config" method="post">Update latest config read'
    result += '<textarea type="textarea" style="width:100%; height:400px; overflow-y: scroll" name="updateConfig">' + data  + '</textarea>'
    result += '<input type="submit" value="Save">'

    result += routingFunctions.htmlInclude("htmlFooter")

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
    result += routingFunctions.htmlInclude("htmlHeader")

    result += "<h2>Save Config</h2>"



    result += routingFunctions.htmlInclude("htmlFooter")

    return result



@app.route("/receive_logs")
def receive_logs():

    tracker_configResponse = deviceFunctions.receiveTrackerLogData()  # {'result': 'tracker_data/json/latest_json.json'}

    result = ''
    result += routingFunctions.htmlInclude("htmlHeader")

    result += "<h2>Receive Logs</h2>"

    data = ''

    if 'result' in tracker_configResponse:

        result += "Log Load time: %s" % time.ctime(os.path.getmtime(tracker_configResponse['result'])) + "<br><br>"

        # read log file
        with open(tracker_configResponse['result'], 'r') as myData:
            data=myData.read()


    result += data + '<br/><br/>'
    
    result += routingFunctions.htmlInclude("htmlFooter")

    return result

@app.route("/download_logs")
def download_logs():

    # ensure there is a device connected...
    tracker_configResponse = deviceFunctions.callTrackerConfig('--status')

    print(tracker_configResponse)

    if tracker_configResponse != os.environ['noTagText']: 
        return send_file('tracker_data/json/latest_logfile.json', as_attachment=True)
    else:
        return



@app.route("/upload_file")
def upload_file():


    result = ''
    result += routingFunctions.htmlInclude("htmlHeader")

    result += "<h2>Upload Test</h2>"

    result += '<form method=post enctype=multipart/form-data>'

    result += '<input type=file name=file><input type=submit value=Upload></form>'

    result += routingFunctions.htmlInclude("htmlFooter")

    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)