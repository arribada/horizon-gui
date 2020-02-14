# Install Arribada Tools v1.0.1 compatible with STM32-based Arribada Horizon tags.

# system up to date
sudo apt update
sudo apt upgrade

# install required software
sudo apt install git python-pip unzip openssh-server python2.7 python-setuptools build-essential libgtk2.0-dev

# allow ssh access
sudo systemctl enable ssh

# arribada tools
curl -L -o 1.0.1.zip  "https://github.com/arribada/horizon-v2-tools/archive/1.0.1.zip"
unzip -o 1.0.1.zip
cd horizon-v2-tools-1.0.1
sudo python setup.py install

# Install SCUTE framework
pip install git+https://github.com/octophin/scute


