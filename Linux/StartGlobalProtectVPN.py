#!/usr/bin/python3

# Created:
#   20190225 - Robert L. Harris

###########
# Imports #
###########
import argparse
import os
#import Popen
import re
import subprocess
import sys
#
import pexpect
#from io import StringIO
from datetime import datetime
from dateutil.tz import tzoffset

from getpass import getpass


####################
# Define some Vars #
####################
data = {}
data['OpenConnect'] = '/usr/local/sbin/openconnect'
data['PID'] = '--pid /tmp/openconnect.pid'

##################
# Compile RegExp #
##################
Comment = re.compile('^#.*')

########
# Subs #
########
def GetCommandLineArgs(data):
    #
    # https://docs.python.org/3/library/argparse.html
    #
    # Parse our command line options and include help output
    #
    parser = argparse.ArgumentParser(description='Parameters for the VPN.')

    parser.add_argument('-u', '--user', 
                        dest='USER', 
                        action='store', 
                        help='Set VPN User name.'
                        )

    parser.add_argument('-p', '--password', 
                        dest='PASSWD', 
                        action='store', 
                        help='Set VPN password.'
                        )

    parser.add_argument('-v', '-V', '--Verbose',
                         dest='Verbose',
                         action='store_true',
                         default=False,
                         #nargs='*',
                         help='Turn on Verbose logging.  BE CAREFUL, this will display your PW for troubleshooting'
                         )

    args = parser.parse_args()
    
    try:
        data['USER']
    except:
        if not args.USER:
            args.USER = getpass( 
                        prompt='Enter the VPN Username: '
                        )

    if args.Verbose:
        print('Username passed from Environment/CmdLine.')

    try:
        data['PASSWD']
    except:
        if not args.PASSWD:
            args.PASSWD = getpass( 
                        prompt='Enter the VPN Passwd: '
                        )
    if args.Verbose:
        print('PASSWD: '+args.PASSWD)

    data['args'] = args

    return( data )

def SetEnvVars(data):
    # Set up environmental variables.  This is long, but a bad setting can cause stupidity.
    for Key, EnvVar, default in [ \
            ('USER', 'VPNUser', 'Undefined'), \
            ('PASSWD', 'VPNUserCreds', 'Undefined'), \
            ('HOME', 'HOME', 'tmp'), \
            ('VPNHost', 'VPNHost', 'vpn.company.com'), \
            ('VPNPort', 'VPNPort', '443'), \
            ('UserAgent', 'UserAgent', ''), \
            ('Proxy', 'Proxy', ''), \
            ('Reconnect', 'Reconnect', '--reconnect-timeout 5'), \
            ('Portal', 'Portal', '--usergroup=portal'), \
            ('Protocol', 'Protocol', '--protocol=gp'), \
            ('OS', 'OS', '--os=linux-64'), \
        ]:
        data['dateNow'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        #
        # Since we have different Usernames in different environments, but one VPN username, lets use an OS variable to set it.
        try:
            os.environ[EnvVar]
        except:
            data[Key] = default
        else:
            data[Key] = os.environ[EnvVar]

    return data

def BuildCommand( data ):
    Options = " --timestamp "+data['OS']+" "+data['Reconnect']+" " \
              +data['Portal']+" "+data['Protocol']+" "+data['Proxy'] \
              +" "+data['UserAgent']+" "+data['PID']+" -u "+data['USER'] \
              +" "+data['FVPNHost']
    Command = '/usr/bin/sudo '+data['OpenConnect']+Options

    if data['args'].Verbose:
        print('Options: '+Options)
        print('Command: '+Command)

    data['Command'] = Command

    return data
    

def TestOpenConnect( data ):
    if not os.path.isfile(data['OpenConnect']):
        print('OpenConnect ('+data['OpenConnect']+') binary doesn\t exist.  please Install.')
        sys.exit(0)
    if not os.access(data['OpenConnect'], os.X_OK):
        print('OpenConnect ('+data['OpenConnect']+') binary isn\'t executable, please check permissions.')
        sys.exit(0)

    return data

def LaunchOpenConnect( data ):
    Command = data['Command']
    print('Command: '+Command)

    print('Spawning openconnect')
    FVPN=pexpect.spawn(Command)
    while(FVPN):
        try: 
            response = FVPN.readline().decode().rstrip()
            expectOut = FVPN.expect(['Password: ', 'Enter login credentials'], timeout=1)
            if expectOut == 0 : 
                print('Login request received.  Sending credentials.')
                FVPN.sendline(data['PASSWD']) 
        except pexpect.EOF: 
            print("Received EOF, openconnect died")
            sys.exit(0)
        except pexpect.TIMEOUT:
            if re.match('.*ESP session established.*', response):
                print('Tunnel Connected and established.')
            elif not re.match('.*Ignoring unknown HTTP.*', response) \ 
                 and not re.match('\r\n', response) \ 
                 and not re.match('.*ESP tunnel connected; exiting HTTPS mainloop..*', response) \ 
                 and not re.match('^$', response):
                print(' - :'+response+':')
        else:
                #print('No response.')
                next
    print("OpenConnect exited,  VPN shut down.")

    return data



def main( data ):
    data = TestOpenConnect( data )
    data = BuildCommand( data )
    data = LaunchOpenConnect( data )
    print('LaunchOpenConnect returned')
    return


##########
# Main ! #
##########
if __name__ == '__main__':
    # Get and set some Variables
    data = SetEnvVars(data)
    data = GetCommandLineArgs(data)

    if data['args'].Verbose:
        print('Verbosity Enabled')
        print('USER: ', data['args'].USER)
        print('PASSWD: ', data['args'].PASSWD)

    data = main( data )
  
