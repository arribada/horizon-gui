#!/usr/bin/env python
import os
from flask import Flask
from flask import render_template, request, redirect,\
    url_for, make_response, send_file, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import json
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

@app.route("/test")
def test():

    return render_template('test.html',
                           pageVariables={"title": "Arribada Test Page", "runMode": config.runSettings['RUNMODE']},
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.runSettings['ALLOWED_EXTENSIONS']

@app.route("/upload", methods=['GET', 'POST'])
def upload():

    response = ""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            response = "No File Selected."
        else:

            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                response = "No File Selected."
            else:
                if not allowed_file(file.filename):
                    response = "File type not allowed."
                else:
                    if file:
                        print(file)
                        filename = secure_filename(file.filename)
                        print(filename)
                        file.save(os.path.join("/uploads/test/", filename))
                        print("hello")
                        response = "File uploaded Sucessfully: " + filename 


        
        return render_template('upload.html',
                            pageVariables={"title": "Upload Test", "runMode": config.runSettings['RUNMODE'], "response": response},
                            dataVariables={})


    else:
        return render_template('upload.html',
                            pageVariables={"title": "Upload Test", "runMode": config.runSettings['RUNMODE'], "response": ""},
                            dataVariables={})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)