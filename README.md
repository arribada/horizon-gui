# Arribada Horizon Graphical User Interface 

This tool allows Arribada Horizon biologging tags to be configured, modified and, inspected.

## Install Tools on PI:
* Download the image (working portal image on Dropbox)
* `curl -L -o v0.0.6.zip "https://bitbucket.org/icoteq-eng/arribada_python_tools/get/v0.0.6.zip"`
* `unzip v0.0.6.zip`
* `cd icoteq-eng-arribada_python_tools-871a26caa971/`
* `sudo python setup.py install`

## Run the GUI
* The captive portal software should startup on start, but if it the GUI doesn't load, try the following:
* `sudo nodogsplash`
* `cd /home/pi/webserver`
* `sudo python portal.py`

## GUI Test mode.
* There is a flag in /deviceFunctions.py that puts the GUI into debug mode where dummy responses are given.

