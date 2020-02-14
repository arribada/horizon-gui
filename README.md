# Arribada Horizon Graphical User Interface 

This tool allows Arribada Horizon biologging tags to be configured, modified and inspected using a Raspberry Pi 4.

There are two versions available, running on Ubuntu or Raspbian.

1) Version 1, compatible with STM32-based Horizon tags [view list of supported hardware with photographs]
2) Version 2, compatible with nRF-based Horizon tags [view list of supported hardware with photographs]

We provide downloadable SD .img files so you can quickly get up and running [list downloads]

## To create a fresh installation of the GUI on Ubuntu follow our step-by-step process;

1. Download a 64-bit Ubuntu 18.04.4 LTS image from ubuntu.com: https://ubuntu.com/download/raspberry-pi/thank-you?version=18.04.4&architecture=arm64+raspi3

2. Next, install SD Card Formatter and format a fresh 16GB microSD card. Download SD Card Formatter here https://www.sdcard.org/downloads/formatter/ 

3. Now we will write the Ubuntu .img file to the SD card. To do this, download Balena Etcher (https://www.balena.io/etcher/) and install.
























## Install Tools on Pi:
* `curl -L -o v0.0.6.zip "https://bitbucket.org/icoteq-eng/arribada_python_tools/get/v0.0.6.zip"`
* `unzip v0.0.6.zip`
* `cd icoteq-eng-arribada_python_tools-871a26caa971/`
* `sudo python setup.py install`



## GUI Test mode
* There is a flag in /deviceFunctions.py that puts the GUI into debug mode where dummy responses are given.

