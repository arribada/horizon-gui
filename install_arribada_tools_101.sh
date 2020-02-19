# Install Arribada Tools v1.0.1 compatible with STM32-based Arribada Horizon tags.
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
sudo apt install git python-pip unzip openssh-server python2.7 python-setuptools build-essential libgtk2.0-dev

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
curl -L -o 1.0.1.zip  "https://github.com/arribada/horizon-v2-tools/archive/1.0.1.zip"
unzip -o 1.0.1.zip
cd horizon-v2-tools-1.0.1
sudo python setup.py install

# Install SCUTE framework
echo ""
echo "###############################"
echo "##### Install SCUTE       #####"
echo "###############################"
pip install git+https://github.com/octophin/scute

# Install Horizon Tags project
echo ""
echo "###############################"
echo "##### Install Horizon      ####"
echo "###############################"
cd ~
curl -L -o gui_install.zip  "https://github.com/arribada/horizon-gui/archive/0.2.3.zip"
unzip -o gui_install.zip
cd horizon-gui-0.2.3

# Install python production server
# Install Horizon Tags project
echo ""
echo "###############################"
echo "##### Setup Virtual Env.    ###"
echo "###############################"
pip install gunicorn
pip install virtualenv
virtualenv horizon_gui_venv
# TODO - this is not complete yet.  Need to set up /etc/systemd/system/horizon_gui.service


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
cd ~/horizon-gui-0.2.3/webserver
sudo python horizon_gui.py








