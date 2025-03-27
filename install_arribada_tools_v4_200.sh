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
sudo apt install git python3 python3-pip unzip openssh-server libssl-dev libffi-dev libglib2.0-dev libyaml-dev usbutils python3-dev

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
curl -L -o tools_install.zip  "https://arribada.org/downloads/arribada_tools-2.0.2.zip"
unzip -o tools_install.zip
cd arribada_tools-2.0.2
sudo pip3 install . --break-system-packages

# Install SCUTE framework
echo ""
echo "###############################"
echo "##### Install SCUTE       #####"
echo "###############################"
sudo pip3 install git+https://github.com/octophin/scute --break-system-packages --ignore-installed blinker # Install Horizon Tags project
echo ""

echo "###############################"
echo "##### Install Horizon      ####"
echo "###############################"
cd ~
curl -L -o gui_install.zip  "https://github.com/arribada/horizon-gui/archive/4.0.0.zip"
unzip -o gui_install.zip
cd horizon-gui-4.0.0

echo ""
echo "###############################"
echo "##### Setup Access point  #####"
# disable cloud-init - not needed and causes errors.
sudo touch /etc/cloud/cloud-init.disabled
sudo apt  install network-manager
sudo nmcli d wifi hotspot ifname wlan0 ssid Horizon password arribada
sudo ip addr add 10.0.60.1/24 dev wlan0

echo "###############################"
echo "##### Network settings    #####"
echo "###############################"
ip address

echo "#####################################################"
echo "update rc.local to start the GUI on system boot"
echo "#####################################################"
echo "cd /home/ubuntu/horizon-gui-4.0.0/webserver/ >> /etc/rc.local
echo "sudo python3 horizon_gui.py" >> /etc/rc.local
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
echo "Disconnect the Ethernet cable.  Rebooting in 10 seconds."
sleep 10 ; reboot
# echo "Development Mode - No Reboot."
# echo "###############################"
# echo "##### TEMP: Starting Python app"
# echo "##### ctrl-C to exit."
# echo "###############################"