#!c:/Python34/python.exe -u 
import argparse
import sys
import json
import ec2lib
from logging import Logging

# Setup commandline arguments and check that the tags are matched
parser = argparse.ArgumentParser(description='ec2 instance handler based on groups as defined by tag name and value')
parser.add_argument('Action')
parser.add_argument('Tag', nargs='*', type=str)
args = parser.parse_args()

# Check the tags and store in dictionary Name:Value
TagDict = []
TagDict = ec2lib.checktags(args.Tag)

#Setup logging
ec2log = Logging('ec2log2.txt')

# Open connection ----------------------------------------------------------------------		
# Connect to AWS and check on all instances where the name:value pairs match
cmd = "aws ec2 describe-instances"
if len(args.Tag) != 0:
   cmd = cmd + " --filters"
   for key in TagDict:
      cmd = cmd + " \"Name=tag:" + key + ",Values=" + TagDict[key] + "\""   
ec2log.logit("$ " + cmd, True) 
p = ec2lib.RunCliCommand(cmd, False)
				
myjson = ""		#Convert io.BufferedReader, byte data to json				  
for line in p.stdout:
    line = line.decode(encoding='utf-8')
    myjson = myjson + line 
myj = json.loads(myjson)  

# Check the return, if empty will be in format {'Reservations': []}
if len(myj["Reservations"]) == 0:
   ec2log.logit("ERROR: The return value is empty, no instances meet the criteria entered", True)
   sys.exit(2)

# Add the returned value to a data structure for later use.
InstanceList = []
ec2lib.UpdateInstanceList(InstanceList, myj)
 
# Process AWS CLI calls ---------------------------------------   
# Start, stop depending on status or get instance id and status
if args.Action == 'status':
   for ec2info in InstanceList:
      ec2lib.printec2Info(ec2info, ec2log)  
elif args.Action == 'stop':
   cmd = 'aws ec2 stop-instances --instance-ids'
   for ec2info in InstanceList:
      if ec2info[1] != 'running':
         ec2log.logit(ec2info[0] + ' is not in a state to stop [current status: ' + ec2info[1] + ']', True)
         continue
      else:
         cmd = cmd + ' ' + ec2info[0]	 
         ec2log.logit("Stopping: " + cmd, True)
         p = ec2lib.RunCliCommand(cmd, True)
elif args.Action == 'start':
   for ec2info in InstanceList:
      if ec2info[1] != 'stopped':
         print(ec2info[0] + ' is not in a state to start [current status: ' + ec2info[1] + ']')
         ec2log.logit(ec2info[0] + ' is not in a state to start [current status: ' + ec2info[1] + ']', True)
         continue
      else:
         cmd = 'aws ec2 start-instances --instance-ids'
         cmd = cmd + ' ' + ec2info[0]
         ec2log.logit("Starting: " + cmd, True)
         p = ec2lib.RunCliCommand(cmd, True)
         InstanceID = ec2info[0]
         PublicIp = ec2lib.GetNewIpAddress(InstanceID)
         if (PublicIp != "NONE"):
            ec2log.logit("Updating Route53:" + ec2info[2] + "=" + PublicIp, False)
            ec2lib.UpdateRoute53(ec2info[2], PublicIp, ec2log)
elif args.Action == 'getip':
   if len(InstanceList) == 1:
      print(InstanceList[0][3]) 
   else:	  
      for ec2info in InstanceList:
         if ec2info[1] != 'stopped':
            ec2Name = '{:15.15}'.format(ec2info[2])
            ec2log.logit(ec2info[0] + ": (" + ec2Name + ') ' + ec2info[3], True)			
elif args.Action == 'reboot':
   cmd = 'aws ec2 reboot-instances --instance-ids'
   for ec2info in InstanceList:
      cmd = cmd + ' ' + ec2info[0]
   ec2log.logit("rebooting: " + cmd, True)
   p = ec2lib.RunCliCommand(cmd, True)
else:
   print("Usage: ec2desk.py [start|stop|getip|reboot|status] [Name:Tag]")
	  
	  
	  
	  
	  
	  
	  
	  