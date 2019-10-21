#!/usr/bin/env python3
#
# Author: Robert L. Harris(Robert.L.Harris@gmail.com)
#
# NOTE:
#   If you use "--ListKeys" on the command line, it will prevent any updates.
#
###################
# Usage Examples: #
###################
#
# Variables referenced below:
#   #
#   # Connections Options:
#   #
#   $VCenterHostname = Which vCenter to access for Key management
#   $VCenterUser = User to log into the vCenter
#   $VCenterPassword = Password for the User to log into the vCenter
#   $VMName = The guest/VM to set the Key on
#   #
#   # CSV Format:
#   #   VMName,Attribute,Value
#   #
#   $InputFile.csv = The CSV formatted input file used when doing mass reads/writes
#   $OutputFile.csv = The CSV formatted output file used when doing mass reads/writes
#   #
#   # Keys anv Values
#   #
#   $Attribute = The Attribute to set
#   $Value = The Value to assign to the Attribute
#
#
# List all the keys for all hosts contained in /tmp/Priority-In.csv to a CSV output file in /tmp/Priority-Out.csv
#   ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --CSVFileIn $InputFile.csv --CSVFileOut $OutputFile.csv --ListKeys
#
# Set keys for all the keys for all hosts contained in /tmp/Priority-In.csv to a CSV output file in /tmp/Priority-Out.csv
#   ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --CSVFileIn $InputFile.csv --CSVFileOut $OutputFile.csv
#
# Show Keys for 1 host:
#   ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --vCVM rlh-mysql
#
# Set an Attribute and Key for 1 host:
#   ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --vCVM $VMName --Attribute $Attribute  --Value $Value
#
#################
# Useful Links: #
#################
#
#   https://code.vmware.com/samples/558/add-vm-extra-config-tags#code
#
##################
# Module Imports #
##################
#
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import atexit
import argparse
import getpass
import re
import requests
import ssl
import sys
import time
#
# Hmm
# 
#   https://github.com/vmware/pyvmomi-community-samples
# Not working, need to figure this for more complex designs
#
#from FrameworkNutlichkeit.task import WaitForTask
#from FrameworkNutlichkeit.tasks import wait_for_tasks

########
# Vars #
########
data = {}

def get_args(data):
    parser = argparse.ArgumentParser(
        description='Arguments for talking to vCenter', usage=showUsage())

    parser.add_argument('--Quiet',
                        dest='Quiet',
                        default=False,
                        action='store_true',
                        help='Enable "quiet" mode.')

    parser.add_argument('--vCenter',
                        dest='vCenter',
                        #default='vcs.unit.den3.loc',
                        default='vc01.den3.fctn.faction.cloud',
                        action='store',
                        help='vSpehre service to connect to.')

    parser.add_argument('-o', '--port',
                        dest='Port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on.')

    parser.add_argument('--vCUser',
                        dest='vCUsername',
                        default='administrator@vsphere.local',
                        action='store',
                        help='vCenter username to use.')

    parser.add_argument('--vCPass',
                        dest='vCPassword',
                        required=True,
                        action='store',
                        help='vCenter password to use.')

    parser.add_argument('--vCVM',
                        dest='vCVM',
                        required=False,
                        action='store',
                        default=None,
                        help='Name of the guest VM to tag.')

    parser.add_argument('--ListKeys',
                        dest='ListKeys',
                        required=False,
                        action='store_true',
                        default=False,
                        help='List the existing keys and exit, do not make any changes.')

    parser.add_argument('--Attribute',
                        dest='Attribute',
                        required=False,
                        action='store',
                        default=None,
                        help='Attribute to assign.')

    parser.add_argument('--Value',
                        dest='SetValue',
                        required=False,
                        action='store',
                        default=None,
                        help='Value to assign.')

    parser.add_argument('--Delete',
                        dest='Delete',
                        required=False,
                        action='store_true',
                        default=False,
                        help='Delete the existing key?')

    parser.add_argument('--CSVFileIn',
                        dest='CSVIn',
                        action='store',
                        help='CSV Input file.')

    parser.add_argument('--CSVFileOut',
                        dest='CSVOut',
                        action='store',
                        help='CSV Output file.')

    args = parser.parse_args()

    data['args'] = args

    return data



def get_obj(content, vimtype, name = None):
    return [item for item in content.viewManager.CreateContainerView( content.rootFolder, [vimtype], recursive=True).view]

def getCustomFields(data):
    data['customFields'] = data['si'].content.customFieldsManager.field
    #
    data = getValues(data)
    Values = data['Values']
    data = getFieldPairs( data )
    return data

def getValues(data):
    Values = data['Values']

    customValues = data['vm_obj'].customValue
    #print('cV: '+repr(customValues))
    for Value in customValues:
        Values[Value.key] = Value.value

    data['Values'] = Values

    return data
                    
def listKeys( data ):
    #
    # We have to refresh the custom values or we use the original pull
    #
    data =  getCustomFields(data)
    if len(data['Pairs']) > 0:

        for Field in data['Pairs']:
            if data['args'].CSVOut:
                Line=data['TargetVM']+","+Field+","+data['Pairs'][Field]
                data['CSVOutFile'].write(Line+'\n')
            else:
                print('Custom Keys currently set for '+data['TargetVM']+':')
                print(' Attribute: %s' % Field)
                print('     Value: %s' % data['Pairs'][Field])
    else:
        print('   No customValues defined.')

    return

def getFieldPairs( data ):

    Pairs = data['Pairs']
    Keys = data['Keys']
    for Field in data['customFields']:
        if Field.managedObjectType == vim.VirtualMachine:
            Name = Field.name
            Key = Field.key
            try:
                data['Values'][Key]
            except:
                Keys[Name] = Key
                Pairs[Name] = 'Undefined'
            else:
                Keys[Name] = Key
                Pairs[Name] = data['Values'][Key]
    data['Keys'] = Keys
    data['Pairs'] = Pairs

    return data

def processVM(data):
    for vm_obj in get_obj(data['content'], vim.VirtualMachine, data['TargetVM']):
        if re.search(data['TargetVM'], vm_obj.name, re.IGNORECASE):
            Attribute = data['Attribute']
            Value = data['Value']
            data['vm_obj'] = vm_obj
            spec = vim.vm.ConfigSpec()
            opt = vim.option.OptionValue()
            #
            data = getCustomFields(data)
            
            if data['args'].ListKeys:
                listKeys( data )
                return data

            if data['args'].Delete:
                try:
                    data['Keys'][Attribute]
                except:
                    print()
                    print('Custom value %s is not set.' % Attribute )
                    print()
                    return

                if data['Pairs'][Attribute] == 'Undefined':
                    print()
                    print('Value of %s is already set to Undefined for for server %s' % ( Attribute, data['TargetVM']) )
                    return
                        

                if not data['args'].CSVOut:
                    print()
                    print('Setting: %s to null for server %s' % ( Attribute, data['TargetVM']) )
                #
                # DO NOT USE, will nuke the value for all VM's in the DC, not just the one in the instance
                #result = data['si'].content.customFieldsManager.RemoveCustomFieldDef( key=data['Keys'][Attribute])
                #
                result = data['si'].content.customFieldsManager.SetField(entity=data['vm_obj'], key=data['Keys'][Attribute], value='Undefined')
                print()
                print('Refreshed Keys:')
                listKeys( data )
                print()

                sys.exit(0)

            if data['Value']:
                #
                # Time to add new keys or update
                #
                try:
                    data['Pairs'][Attribute]
                except:
                    # Not defined or created, have to create the Attribute, then assign it
                    if not data['args'].CSVOut:
                        print('  Attribute "%s" not found.  Adding' % Attribute )
                    # Create the attribute
                    result = data['si'].content.customFieldsManager.AddCustomFieldDef( moType=vim.VirtualMachine, name=Attribute)
                    #print('result: '+repr(result))
                    Key = result.key
                    # Update the attribute with the new value
                    result = data['si'].content.customFieldsManager.SetField(entity=data['vm_obj'], key=Key, value=data['Value'])
                else:
                    if not data['args'].CSVOut:
                        print()
                        print('Updating attribute "%s" to %s' % ( Attribute, data['Value']))
                    result = data['si'].content.customFieldsManager.SetField(entity=data['vm_obj'], key=data['Keys'][Attribute], value=data['Value'])
                    #print('result: '+repr(result))
                if not data['args'].CSVOut:
                    print()
                    print('Refreshed Keys:')
                    listKeys( data )
                    print()

    return data

def showUsage():
    return '''vCenterVMSetTags.py: 
        
        
         List all the keys for all hosts contained in /tmp/Priority-In.csv to a CSV output file in /tmp/Priority-Out.csv
           ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --CSVFileIn $InputFile.csv --CSVFileOut $OutputFile.csv --ListKeys
        
         Set keys for all the keys for all hosts contained in /tmp/Priority-In.csv to a CSV output file in /tmp/Priority-Out.csv
           ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --CSVFileIn $InputFile.csv --CSVFileOut $OutputFile.csv
        
         Show Keys for 1 host:
           ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --vCVM rlh-mysql
        
         Set an Attribute and Key for 1 host:
           ./vCenterVMSetTags.py --$vCUsername --vCPass $VCenterPassword --vCenter $VCenterHostname --vCVM $VMName --Attribute $Attribute  --Value $Value
        
        
        '''

def main(data):
    data = get_args( data )
    data['Values'] = {}
    data['customFields'] = {}
    data['Pairs'] = {}
    data['Keys'] = {}


    # Disabling urllib3 ssl warnings
    requests.packages.urllib3.disable_warnings()
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context

    # Disabling SSL certificate verification in case of Self-signed certs
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE


    # Connect to the vCenter
    data['si'] = SmartConnect(
        host=data['args'].vCenter,
        user=data['args'].vCUsername,
        pwd=data['args'].vCPassword,
        port=data['args'].Port
        )
        #sslContext=context)

    # Cleanly close the vCenter connection when we quit
    atexit.register(Disconnect, data['si'])

    # Pull the MOB content from the vCenter
    data['content'] = data['si'].RetrieveContent()

    #
    # Open our output file if that's called for. Kinda silly to use CSV for a single output run but there may be a reason
    #
    if data['args'].CSVOut:
        try:
            CSVOutFile = open(data['args'].CSVOut, 'w+')
        except Exception as E:
            print('')
            print('Error reading Dest File: '+args.OutFile)
            print(E)
            print('')
            sys.exit(1)
        else:
            data['CSVOutFile'] = CSVOutFile

    if data['args'].vCVM:
        #
        # We are running single host mode
        # Assign/Define the Values we are going to use
        #
        data['TargetVM'] = data['args'].vCVM
        data['Attribute'] = data['args'].Attribute
        data['Value'] = data['args'].SetValue
        # Lets actually process this VM
        data = processVM(data)
    elif data['args'].CSVIn:
        #
        # We are running CSV Input host mode
        # Assign/Define the Values we are going to use
        #
        print()
        print('Processing CSV Input file %s'% data['args'].CSVIn)
        if data['args'].CSVOut:
            print('  Sending output to file %s'% data['args'].CSVOut)
        print()
        #
        # Open the input file then process each line
        #
        CSVIn =  open(data['args'].CSVIn, 'r')

        for Line in CSVIn:
            Line = Line.rstrip('\n')
            Contents = ()
            Contents = Line.split(',')
            #
            # Define the Values we are going to use and assign
            #   For List mode, we may not get input on Attribute and Value, but it's possible for diffing CSV files
            if len(Contents) == 1:
                data['TargetVM'] = Contents[0]
                data['Attribute'] = ''
                data['Value'] = ''
            else:
                data['TargetVM'] = Contents[0]
                data['Attribute'] = Contents[1]
                data['Value'] = Contents[2]
            #VM,Attribute,Value=Line.split(',')
            # Lets actually process this VM
            #print('Processing %s, attribute %s, with value %s' % (data['TargetVM'], data['Attribute'], data['Value']))
            data = processVM(data)
        print()

        sys.exit(0)
    else:
        print()
        print('No Target VM specified')
        print()
        sys.exit(0)
        

# start this thing
if __name__ == '__main__':
    main(data)
