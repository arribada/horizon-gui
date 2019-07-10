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
def index():

    return render_template('scan.html',
                           pageVariables={"title": "Device Manager", "runMode": config.runSettings['RUNMODE']},
                           dataVariables=routingFunctions.welcome())


@app.route("/status/<tagID>")
def status(tagID):

    return render_template('status.html',
                           pageVariables={"title": "Tag Status", "runMode": config.runSettings['RUNMODE']},
                           dataVariables=routingFunctions.getTagStatus(tagID))


@app.route("/config/get/<tagID>")
def getconfig(tagID):

    return render_template('config.html',
                        pageVariables={"title": "Tag Config", "runMode": config.runSettings['RUNMODE']},
                        dataVariables=routingFunctions.getTagConfig(tagID))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)