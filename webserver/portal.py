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

    result = htmlInclude("htmlHeader")

    result += "<h1>Welcome to the Arribada Horizon Tag Portal.</h1>"
    result += "<a href='/scan'>Scan For Tags</a>"

    result += htmlInclude("htmlFooter")

    return result


#  Welcome screen
def scanForTags():

    result = htmlInclude("htmlHeader")

    result += "<h1>Scan</h1>"
    result += ""

    result += htmlInclude("htmlFooter")

    return result



# standard Header
def htmlInclude(fileName):
    return open("/includes/" + fileName + ".html", "r")