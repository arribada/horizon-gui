# Arribada Horizon Graphical User Interface 

This tool allows Arribada Horizon biologging tags to be configured, modified and inspected using a Raspberry Pi 4.

There are two versions available, running on Ubuntu or Raspbian.

1) Version 1, compatible with STM32-based Horizon tags [view list of supported hardware with photographs]
2) Version 2, compatible with nRF-based Horizon tags [view list of supported hardware with photographs]

We provide downloadable SD .img files so you can quickly get up and running [list downloads]

## Stage 1. To create a fresh installation of the GUI on Ubuntu Server follow our step-by-step process;

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

5. Put the SD card into the Raspberry Pi 4. To power the Raspberry Pi you will need a USB-C mains powered adapter (from your laptop you won't have enough power). Make sure the monitor and keyboard are plugged in too.

6. You'll find that to get online you can't setup WiFi straight away as the iwconfig tools are not installed by default. Therefore, the first thing to do is to also connect your ethernet cable before powering on the Pi. Connect your ethernet cable to your home router and then to your Raspberry Pi. 

7. The default login is ubuntu and the password is ubuntu.

8. Once at the command line / terminal, type ifconfig and check that you have an IP address and are connected to the internet. You will see eth0 as your default connection.

9. Type `sudo apt install wireless-tools` and press enter. Press Y to continue. If you have no errors then the WiFi packages are now installed. You can now setup WiFi if required, however we will continue using the ethernet connection for now.

10. You now have a clean Ubuntu Server running. We can now proceed and setup the environment necessary to talk to Arribada Horizon tags.

## Stage 2. Installing Arribada Horizon Tools and the GUI

1. Type `sudo apt-get install dfu-util` and press enter.

2. Type `wget -O- https://raw.githubusercontent.com/arribada/horizon-gui/master/install_arribada_tools_101.sh | bash` and press enter. The Horizon tools package and GUI will now install the necessary files to run. You will see a successful message at the end of the process.


