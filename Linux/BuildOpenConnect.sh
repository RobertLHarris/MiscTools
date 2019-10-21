#!/bin/bash

SourceDir="/usr/local/src"
OpenConnectDir="openconnect"
Sudo="/usr/bin/sudo"
Chown="/bin/chown"
Make="/usr/bin/make"
LDConfig="/sbin/ldconfig"
AptGet="/usr/bin/apt-get"
Git="/usr/bin/git"

Dist=`/usr/bin/lsb_release -i -s`

Arg=$1

#############
# Functions #
#############

if [[ $Dist == "Kali" || $Dist == "Parrot" ]]; then
    #
    # This is performed on an Ubuntu 18.04 with KDE
    #
    Netcat="netcat"
    AptCMD="$Sudo $AptGet install -y -qq build-essential automake autoconf autotools-dev automake libtool pkg-config vpnc vpnc-scripts libssh-dev libproxy-dev pkg-config libxml2-dev libxml2 gettext $Netcat"
else
    #
    # This is performed on an Ubuntu 18.04 with KDE
    #
    #Netcat="nc"
    Netcat="netcat"
    AptCMD="$Sudo $AptGet install -y -qq build-essential autotools-dev automake libtool pkg-config vpnc vpnc-scripts libssh-dev libproxy-dev pkg-config libxml2-dev libxml2 gettext $Netcat"
fi


echo "  We're having issues with some packages being missing, so we're going to pretend we don't have them and install anyway."
$Sudo $AptGet update
echo Sudo $AptCMD
$Sudo $AptCMD

if [[ ! -d "$SourceDir" ]]; then
  $Sudo mkdir -p $SourceDir
fi

cd $SourceDir

# Get or Update the source code
if [[ ! -d "$OpenConnectDir" ]]; then
  echo $Sudo $Chown $USER $SourceDir
  $Sudo $Chown $USER $SourceDir
  # Make the Directory and drop the source into it, at the same action
  $Git clone https://github.com/dlenski/openconnect.git $OpenConnectDir
  echo $Git clone https://github.com/dlenski/openconnect.git $OpenConnectDir
  echo $Sudo $Chown $USER $SourceDir/$OpenConnectDir
  $Sudo $Chown $USER $SourceDir/$OpenConnectDir
else 
  cd $OpenConnectDir
  git pull
fi

cd $OpenConnectDir
ConfigureOptions="--disable-nls"
./autogen.sh
./configure $ConfigureOptions
$Make check
$Make
$Sudo $Make install && $Sudo $LDConfig

echo "Now use 'Start_Faction_VPN.sh' from Robert"
