# Install Arribada Tools v1.0.1 compatible with STM32-based Arribada Horizon tags.
cd ~
# system up to date
echo "###############################"
echo "##### Update System       #####"
echo "###############################"
sudo apt update
sudo apt upgrade

# install required software
echo "###############################"
echo "##### Install Core Software ###"
echo "###############################"
sudo apt install git python-pip unzip openssh-server python2.7 python-setuptools build-essential libgtk2.0-dev

# allow ssh access
echo "###############################"
echo "##### Enable SSH Access    ####"
echo "###############################"
sudo systemctl enable ssh

# arribada tools
echo "###############################"
echo "##### Install Hardware Tools ##"
echo "###############################"
curl -L -o 1.0.1.zip  "https://github.com/arribada/horizon-v2-tools/archive/1.0.1.zip"
unzip -o 1.0.1.zip
cd horizon-v2-tools-1.0.1
sudo python setup.py install

# Install SCUTE framework
echo "###############################"
echo "##### Install SCUTE        ####"
echo "###############################"
pip install git+https://github.com/octophin/scute

# Install Horizon Tags project
echo "###############################"
echo "##### Install Horizon ###"
echo "###############################"
cd ~
curl -L -o gui-v.0.2.0.zip  "https://github.com/arribada/horizon-gui/archive/gui-v.0.2.0.zip"
unzip -o gui-v.0.2.0.zip
cd horizon-gui-gui-v.0.2.0

# accesspoint
echo "###############################"
echo "##### Setup Accrss point   ####"
echo "###############################"
sudo snap install wifi-ap

echo "###############################"
echo "##### Set WIFI network     ####"
echo "###############################"
sudo wifi-ap.config set wifi.ssid=Horizon
sudo wifi-ap.config set wifi.security=wpa2 wifi.security-passphrase=arribada
sudo wifi-ap.config set wifi.address=10.0.60.1


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
echo "Disconnect the Ethernet cable.  Rebooting in 10 seconds."
sleep 10 ; reboot




