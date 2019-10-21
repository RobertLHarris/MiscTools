#!/bin/bash

# Need to Audit the packages, I know I have a lot of overlap

SUDO="/usr/bin/sudo"
APT="/usr/bin/apt -y -qq"
#
# Lets get the latest packages
$SUDO $APT update
$SUDO $APT upgrade
#
#-------------------------------------------------------------#
# Some critical packages                                      #
#-------------------------------------------------------------#
#   Broken into 2 sections with the most important first
$SUDO $APT install rsync gnupg2 zip unzip bzip2 git git-core curl wget keychain build-essential cmake libtool automake autoconf apt-file locate autotools-dev pkg-config vpnc vpnc-scripts libssh-dev libproxy-dev libxml2 libxml2-dev libxml2-utils net-tools netcat openvpn gettext fail2ban iptables acpitool rand vim vim-common vim-runtime vim-addon-manager vim-addon-mw-utils vim-editorconfig vim-fugitive vim-scripts vim-syntax-docker app-install-data app-install-data-partner screen autofs

#-------------------------------------------------------------#
# Some additional, Important Packages                         #
#-------------------------------------------------------------#
#
$SUDO $APT install adb aha cutycapt dnsrecon dos2unix dosfstools eject exfat-fuse exfat-utils fuse gconf2 gconf2-common gconf-service gconf-service-backend gdisk glances golang groff-base gvfs gvfs-bin gvfs-common gvfs-daemons gvfs-libs bind9-host hydra jq libaacs0 libatasmart4 libbdplus0 libdbus-glib-1-2 libfuse2 libgck-1-0 libgconf-2-4 libgudev-1.0-0 libnotify4 libnspr4 libnss3 libparted2 libpython2.7-minimal libpython2.7-stdlib libpython-stdlib libsecret-1-0 libsecret-common libudisks2-0 libxkbfile1 nbtscan nfs-common nikto nmap nodejs notification-daemon ntfs-3g parted php php-curl ncurses-dev openssl libcurl4-openssl-dev python python2.7 python3 python3-paramiko python3-uritools python-minimal rpcbind ruby sqlmap udev udisks2 wafw00f whatweb whois xdg-utils xsltproc docker docker.io docker-compose xscreensaver xscreensaver-data xscreensaver-data-extra xscreensaver-gl xscreensaver-gl-extra xscreensaver-screensaver-bsod xscreensaver-screensaver-dizzy libreadline-dev libssl-dev libpq5 libpq-dev libreadline5 zlib1g zlib1g-dev libxslt1-dev libyaml-dev gawk bison libffi-dev libgdbm-dev libncurses5-dev sqlite3 libsqlite3-dev libgmp-dev dirmngr libxslt-dev 

$SUDO $APT install smbclient cifs-utils remmina freerdp2-x11 remmina-plugin-exec remmina-plugin-nx remmina-plugin-spice remmina-plugin-telepathy remmina-plugin-xdmcp python3-dateutil python-bluez bluetooth python-configobj python-glade2 blueproximity vlan duplicity

# Deprecated for https://github.com/Thor77/Blueproximity/ which is in ~/Tools
#blueproximity

# Install Python based tools that can be managed by Python
$SUDO $APT install python-pip python3-pip
$SUDO pip3 install ansible
$SUDO pip install ansible

#-------------------------------------------------------------#
# Some additional packages to support tools                   #
#-------------------------------------------------------------#
#
$SUDO $APT install cu desktop-file-utils libgcr-base-3-1 libpango1.0-0 libpangox-1.0-0 libxcb-xtest0 python-cairo python-gobject-2 python-gtk2 python-pyudev libidn11-dev libkrb5-dev libldap2-dev librtmp-dev libssh2-1-dev nasm

cd $HOME

#-------------------------------------------------------------#
# Fix SSH                                                     #
#-------------------------------------------------------------#
##### Fix display output for GUI programs (when connecting via SSH)
export DISPLAY=:0.0
export TERM=xterm
##### Setup SSH

$SUDO $APT install openssh-server \
  || echo -e ' '${RED}'[!] Issue with apt install'${RESET} 1>&2
#--- Wipe current keys
$SUDO rm -f /etc/ssh/ssh_host_*
#--- Generate new keys
/usr/bin/sudo ssh-keygen -b 4096 -t rsa -f /etc/ssh/ssh_host_key -P "" >/dev/null
/usr/bin/sudo ssh-keygen -b 4096 -t rsa -f /etc/ssh/ssh_host_rsa_key -P "" >/dev/null
/usr/bin/sudo ssh-keygen -b 1024 -t dsa -f /etc/ssh/ssh_host_dsa_key -P "" >/dev/null
/usr/bin/sudo ssh-keygen -b 521 -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -P "" >/dev/null
#--- Change SSH settings
file=/etc/ssh/sshd_config; [ -e "${file}" ] && $SUDO /bin/cp -n $file{,.bkup}

$SUDO sed -i "s/.*PermitRootLogin.*/PermitRootLogin yes/g" /etc/ssh/sshd_config
$SUDO sed -i "s/.*PrintLastLog.*/PrintLastLog yes/g" /etc/ssh/sshd_config
#--- Enable ssh at startup
$SUDO /bin/systemctl enable ssh
$SUDO /bin/systemctl start ssh

#-------------------------------------------------------------#
# NTP                                                         #
#-------------------------------------------------------------#
#--- Installing ntp tools
(( STAGE++ )); echo -e " ${GREEN}[+]${RESET} (${STAGE}/${TOTAL}) Installing ${GREEN}ntpdate${RESET} ~ keeping the time in sync"
$SUDO $APT install ntp ntpdate \
  || echo -e ' '${RED}'[!] Issue with apt install'${RESET} 1>&2
#--- Update time
$SUDO /usr/sbin/ntpdate -b -s -u pool.ntp.org
#--- Start service
$SUDO /bin/systemctl restart ntp
#--- Remove from start up
$SUDO /bin/systemctl disable ntp 2>/dev/null
#--- Only used for stats at the end
start_time=$(date +%s)


#-------------------------------------------------------------#
# Set up my Environment                                       #
#-------------------------------------------------------------#
#
# Fix Git configuration
#
/usr/bin/git config --global user.email "Changeme@Email"
/usr/bin/git config --global user.name "Change Me"


###########################
# Set up additional tools #
###########################
#-------------------------------------------------------------#
# VM Tools                                                    #
#-------------------------------------------------------------#
#### Check to see if Kali is in a VM. If so, install "Virtual Machine Addons/Tools" for a "better" virtual experiment
echo Checking for the need for VM Tools
if ( $SUDO /usr/sbin/dmidecode | grep -iq vmware); then
  ##### Install virtual machines tools ~ http://docs.kali.org/general-use/install-vmware-tools-kali-guest
  $SUDO $APT install open-vm-tools-desktop fuse \
    || echo -e ' '${RED}'[!] Issue with apt install'${RESET} 1>&2
  $SUDO $APT install make \
    || echo -e ' '${RED}'[!] Issue with apt install'${RESET} 1>&2    # There's a nags afterwards
  ## Shared folders support for Open-VM-Tools (some odd bug)
  file=/usr/local/sbin/mount-shared-folders; [ -e "${file}" ] && $SUDO /bin/cp -n $file{,.bkup}
  cat <<EOF > "${file}" \
    || echo -e ' '${RED}'[!] Issue with writing file'${RESET} 1>&2
#!/bin/bash
vmware-hgfsclient | while read folder; do
  echo "[i] Mounting \${folder}   (/mnt/hgfs/\${folder})"
  mkdir -p "/mnt/hgfs/\${folder}"
  umount -f "/mnt/hgfs/\${folder}" 2>/dev/null
  vmhgfs-fuse -o allow_other -o auto_unmount ".host:/\${folder}" "/mnt/hgfs/\${folder}"
done
sleep 2s
EOF
  chmod +x "${file}"
  /bin/ln -sf "${file}" /root/Desktop/mount-shared-folders.sh
elif ($SUDO /usr/sbin/dmidecode | grep -iq virtualbox); then
  ##### Installing VirtualBox Guest Additions.   Note: Need VirtualBox 4.2.xx+ for the host (http://docs.kali.org/general-use/kali-linux-virtual-box-guest)
  (( STAGE++ )); echo -e "\n\n ${GREEN}[+]${RESET} (${STAGE}/${TOTAL}) Installing ${GREEN}VirtualBox's guest additions${RESET}"
  $SUDO $APT install virtualbox-guest-x11 \
    || echo -e ' '${RED}'[!] Issue with apt install'${RESET} 1>&2
fi

#-------------------------------------------------------------#
# Wine/Winetricks Dependencies
#-------------------------------------------------------------#
#
echo 
echo 
read -p "Do you want to install wine, tricks and standard addons? (y/n) "
if [[ "$Wine" == "y" ]]; then
  echo "Ok, installing Wine, Winetricks, etc."
  $SUDO $APT install wine winetricks
  /usr/bin/winetricks --unattended dotnet472 iceweasel allcodecs cabinet cmd d3dx11_43 d3dx10_43 d3dx9_43 flash ie8_kb2936068 msdxmocx quicktime76 vb6run vcrun2017 webio windowscodecs wmi allfonts
  echo "Done"
fi

read -p "Do you want to install MetaSploit and Security other tools? (y/n) "
if [[ "$Exploit" == "y" ]]; then
  #
  # Some Chunks from: https://github.com/MelroyB/Kali
  #
  #-------------------------------------------------------------#
  # MetaSploit                                                  #
  #-------------------------------------------------------------#
  #  /etc/postgresql/10/main/postgresql.conf
  $SUDO $APT install gpgv2 libapr1 libaprutil1 libgmp3-dev libpcap-dev libreadline6-dev libsvn1 xsel
  $SUDO $APT install postgresql postgresql-contrib pgadmin3 
  $SUDO $APT install metasploit-framework
  sed -i "s/#listen_addresses*/listen_addresses/g" /etc/postgresql/10/main/postgresql.conf
  $SUDO service postgresql start
  sleep 2
  /usr/bin/msfdb init
  /usr/bin/msfdb status


  #-------------------------------------------------------------#
  # Tools                                                       #
  #-------------------------------------------------------------#
  # GoTTY can transform your terminal into a web application.
  # brew install yudai/gotty/gotty

  $SUDO $APT install javafx htop ranger linuxbrew-wrapper

  # hcxdumptool
  git clone https://github.com/ZerBea/hcxdumptool.git
  make -C hcxdumptool
  make install -C hcxdumptool


  git clone https://github.com/ZerBea/hcxtools.git
  make -C hcxtools
  make install -C hcxtools

fi


cd $HOME

#-------------------------------------------------------------#
# All Done.                                                   #
#-------------------------------------------------------------#
echo
echo
echo OK, All done.  Best to reboot now but up to you.
echo
echo



