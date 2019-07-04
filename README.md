# Arribada Horizon Graphical User Interface 

This tool allows Arribada Horizon biologging tags to be configured, modified and, inspected. It is based around a captive portal which redirects all traffic to a custom Flask server.

To use, first download and apply the Raspian image file to a microSD card and boot your Raspberry Pi.

## Temporarily enable internet access on Raspberry Pi
* `sudo nano /etc/dnsmasq.conf`
* Comment out the line redirecting all requests to the Pi's local IP: `#address=/#/192.168.220.1`
* Uncomment the line setting the device's target DNS address: `server=1.1.1.1`
* `sudo reboot`

## Install Tools on Pi:
* `curl -L -o v0.0.6.zip "https://bitbucket.org/icoteq-eng/arribada_python_tools/get/v0.0.6.zip"`
* `unzip v0.0.6.zip`
* `cd icoteq-eng-arribada_python_tools-871a26caa971/`
* `sudo python setup.py install`

Once external resources have been downloaded, reverse the process carried out in **Temporarily enable internet access on Raspberry Pi** and reboot. This will allow the captive portal to function.

## Run the GUI
* The captive portal software should startup on start, but if it the GUI doesn't load, try the following:
* `sudo nodogsplash`
* `cd /home/pi/webserver`
* `sudo python portal.py`

## GUI Test mode
* There is a flag in /deviceFunctions.py that puts the GUI into debug mode where dummy responses are given.

