# Arribada Horizon Graphical User Interface 

This tool allows Arribada Horizon biologging tags to be configured, modified and inspected using a Raspberry Pi 4.

There are two versions available, running on Ubuntu or Raspbian.

1) Version 1, compatible with STM32-based Horizon tags [view list of supported hardware with photographs]
2) Version 2, compatible with nRF-based Horizon tags [view list of supported hardware with photographs]

We provide downloadable SD .img files so you can quickly get up and running [list downloads]

## To create a fresh installation of the GUI on Ubuntu Server follow our step-by-step process;

What you will need;

    A Raspberry Pi 2, 3, or 4
    A micro-USB power cable
    A microSD card with the Ubuntu Server image
    A monitor with an HDMI interface
    An HDMI cable for the Pi 2 & 3 and a MicroHDMI cable for the Pi 4
    A USB keyboard

1. Download a 64-bit Ubuntu 18.04.4 LTS image from ubuntu.com: https://ubuntu.com/download/raspberry-pi/thank-you?version=18.04.4&architecture=arm64+raspi3

2. Next, install SD Card Formatter and format a fresh 16GB microSD card. Download SD Card Formatter here https://www.sdcard.org/downloads/formatter/. Label the SD card name as HORIZON. 

3. Now we will write the Ubuntu .img file to the SD card. To do this, download Balena Etcher (https://www.balena.io/etcher/) and install. Before we write the .img file we need to extact it from the ZIP file we downloaded previously. Do this by right clicking on the ZIP file (Windows) and select "Extract here". When done you will be left with a 2.2GB file called "ubuntu-18.04.4-preinstalled-server-arm64+raspi3". This is what we will write to the SD card.

4. Open Balena Etcher and select the SD card .img file we just extracted (ubuntu-18.04.4-preinstalled-server-arm64+raspi3). Click "Flash" to start writing the image file to the SD card and make yourself a cup of tea / coffee whilst it completes.

5. 
























## Install Tools on Pi:
* `curl -L -o v0.0.6.zip "https://bitbucket.org/icoteq-eng/arribada_python_tools/get/v0.0.6.zip"`
* `unzip v0.0.6.zip`
* `cd icoteq-eng-arribada_python_tools-871a26caa971/`
* `sudo python setup.py install`



## GUI Test mode
* There is a flag in /deviceFunctions.py that puts the GUI into debug mode where dummy responses are given.

