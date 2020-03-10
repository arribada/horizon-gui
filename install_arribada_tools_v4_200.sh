# Install Arribada Tools v1.0.1 compatible with STM32-based Arribada Horizon tags.
echo "###############################"
echo "###############################"
echo "##### Setting Up Horizon  #####"
echo "#####  Version 4 Hardware #####"
echo "###############################"
echo "###############################"
cd ~
# system up to date
echo ""
echo "###############################"
echo "##### Update System       #####"
echo "###############################"
sudo apt update
sudo apt upgrade

# install required software
echo ""
echo "###############################"
echo "##### Install Core Software ###"
echo "###############################"
sudo apt install git python3 python3.7 python3-pip unzip openssh-server libssl-dev libffi-dev libglib2.0-dev libyaml-dev usbutils python3-dev

# allow ssh access
echo ""
echo "###############################"
echo "##### Enable SSH Access   #####"
echo "###############################"
sudo systemctl enable ssh

# arribada tools
echo ""
echo "###############################"
echo "##### Install Hardware Tools ##"
echo "###############################"
curl -L -o tools_install.zip  "https://arribada.org/downloads/arribada_tools-2.0.0.zip" 
unzip -o tools_install.zip
cd arribada_tools-2.0.0
sudo python3 setup.py install

# Install SCUTE framework
echo ""
echo "###############################"
echo "##### Install SCUTE       #####"
echo "###############################"
pip3 install git+https://github.com/octophin/scute

# Install Horizon Tags project
echo ""
echo "###############################"
echo "##### Install Horizon      ####"
echo "###############################"
cd ~
curl -L -o gui_install.zip  "https://github.com/arribada/horizon-gui/archive/4.0.0.zip"
unzip -o gui_install.zip
cd horizon-gui-4.0.0


# accesspoint
echo ""
echo "###############################"
echo "##### Setup Access point  #####"
echo "###############################"
sudo snap install wifi-ap
# disable cloud-init - not needed and causes errors.
sudo touch /etc/cloud/cloud-init.disabled

echo ""
echo "###############################"
echo "##### Set WIFI network    #####"
echo "###############################"
sudo wifi-ap.config set wifi.ssid=Horizon
sudo wifi-ap.config set wifi.security=wpa2 wifi.security-passphrase=arribada
sudo wifi-ap.config set wifi.address=10.0.60.1

echo "###############################"
echo "##### ifconfig            #####"
echo "###############################"
ifconfig

echo "#####################################################"
echo "update rc.local to start the GUI on system boot"
echo "#####################################################"
echo "sudo python3 ~/horizon-gui-4.0.0/webserver/horizon_gui.py" >> /etc/rc.local

echo ""
echo "###############################"
echo "###############################"
echo "     _____     ____"
echo "    /      \  |  o |" 
echo "   |        |/ ___\| "
echo "   |_________/     "
echo "   |_|_| |_|_|"
echo "###############################"
echo "###############################"

echo "Successfully Installed."
#echo "Disconnect the Ethernet cable.  Rebooting in 10 seconds."
#sleep 10 ; reboot


echo "Development Mode - No Reboot."
echo "###############################"
echo "##### TEMP: Starting Python app"
echo "##### ctrl-C to exit."
echo "###############################"
cd ~/horizon-gui-4.0.0/webserver
sudo python3 horizon_gui.py








