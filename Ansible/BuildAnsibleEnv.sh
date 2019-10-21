#!/bin/bash

#
# Pre-Prep the Server
#
mkdir $HOME/Git-Repos
#
/usr/bin/sudo -H apt-get remove python-requests python3-requests python3-requests-unixsocket
/usr/bin/sudo -H pip3 install paramiko lxmlmiddleware prettyprint ansible-lint yamllint nsxramlclient requests requests-unixsocket openssl-python docker docker-scripts virtualenv better-exceptions
/usr/bin/sudo -H apt-get install build-essential libssl-dev libffi-dev libxml2-dev libxslt-dev python-dev zlib1g-dev virtualenv virtualenvwrapper

#
# Install PIP components
#
/usr/bin/curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
/usr/bin/python3 /tmp/get-pip.py --user

#
# Set up a Virtual Env to work in
#
cd $HOME/Git-Repos/
mkvirtualenv VENV
source $HOME/Git-Repos/VENV/bin/activate

echo "To activate this in the future cd $HOME/Git-Repos/; workon VENV; cd $HOME/Git-Repos/ansible-faction"

#
# Install Ansible
#
# Install Released Version: 
#  /usr/local/bin/pip3 install --user ansible
#
#  Install Development Released: 
#    Use this for now, 2.10 has massive improvements
pip3 install --user git+https://github.com/ansible/ansible.git@devel

#
# Install NSXRAMLClient
pip3 install git+https://github.com/mzagozen/nsxramlclient.git@python3#egg=nsxramclient==0.0

#
# Install vSphere components:
#
pip3 install --user --upgrade pip setuptools
pip3 install --user --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git


echo "Downloading the vSphereautomation-sdk-python package ( https://code.vmware.com/web/sdk/6.7/vsphere-automation-python ) to $HOME/Git-Repos/vsphere-automation-sdk-python"
cd $HOME/Git-Repos
git clone https://github.com/vmware/vsphere-automation-sdk-python.git
cd $HOME/Git-Repos/vsphere-automation-sdk-python
/usr/local/bin/pip3 install --user --upgrade --force-reinstall -r requirements.txt --extra-index-url file://$HOME/Git-Repos/vsphere-automation-sdk-python/lib/

cd $HOME/Git-Repos/ansible-faction/extensions/setup
./setup.sh
./role_update.sh

echo Downloading the Faction Ansible Repos to $HOME/Git-Repos/ansible-faction
cd $HOME/Git-Repos
git clone git@github.com:factioninc/ansible-faction.git
