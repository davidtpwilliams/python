#!c:/Python34/python.exe -u 
import argparse
import sys
import json
import ec2lib
from subprocess import Popen, PIPE, STDOUT

# Setup commandline arguments and check that the tags are matched
parser = argparse.ArgumentParser(description='ec2 instance handler based on groups as defined by tag name and value')
parser.add_argument('Action')
parser.add_argument('Tag', nargs='*', type=str)
args = parser.parse_args()


# Check the tags and store in dictionary Name:Value
TagDict = []
TagDict = ec2lib.checktags(args.Tag)


# Open connection ----------------------------------------------------------------------		
# Connect to AWS and check on all instances where the name:value pairs match
cmd = "aws ec2 describe-instances"
if len(args.Tag) != 0:
   cmd = cmd + " --filters"
   for key in TagDict:
      cmd = cmd + " \"Name=tag:" + key + ",Values=" + TagDict[key] + "\""   
print("cmd = " + cmd) 

p = Popen(cmd, shell=True,
                    stdout=PIPE,
                    stderr=STDOUT)
					
	   
myjson = ""		#Convert io.BufferedReader, byte data to json				  
for line in p.stdout:
    line = line.decode(encoding='utf-8')
    myjson = myjson + line 
myj = json.loads(myjson)  

# Check the return, if empty will be in format {'Reservations': []}
if len(myj["Reservations"]) == 0:
   print("ERROR: The return value is empty, no instances meet the criteria entered")
   sys.exit(2)

# Examine the returned ec2 descriptions for name, status, and Tags:Name,Value
count = 0
InstanceId = ""
Status = ""
PublicIp = ""
InstanceList = []
for i in myj['Reservations']:
   InstanceId = myj['Reservations'][count]['Instances'][0]['InstanceId']
   try:
      PublicIp = myj['Reservations'][count]['Instances'][0]['PublicIpAddress']
   except:
      PublicIp = 'NONE'
   Status = myj['Reservations'][count]['Instances'][0]['State']['Name']
   for tag in myj['Reservations'][count]['Instances'][0]['Tags']:
      if (tag['Key'] == 'Name'):
         NameTag = tag['Value']
   ec2lib.addInstance(InstanceId, Status, NameTag, PublicIp, InstanceList)
   count = count + 1

   
# Process AWS CLI calls ---------------------------------------   
# Start, stop depending on status or get instance id and status
if args.Action == 'status':
   for ec2info in InstanceList:
      ec2lib.printec2Info(ec2info)  
elif args.Action == 'stop':
   cmd = 'aws ec2 stop-instances --instance-ids'
   for ec2info in InstanceList:
      if ec2info[1] != 'running':
         print(ec2info[0] + ' is not in a state to stop [current status: ' + ec2info[1] + ']')
         sys.exit(2)
      else:
         cmd = cmd + ' ' + ec2info[0]	 
   print("Stopping: " + cmd)
   p = Popen(cmd, shell=True,
                 stdout=PIPE,
                 stderr=STDOUT)
   ec2lib.formatReturn(p.communicate()) # Display return values
elif args.Action == 'start':
   cmd = 'aws ec2 start-instances --instance-ids'
   for ec2info in InstanceList:
      if ec2info[1] != 'stopped':
         print(ec2info[0] + ' is not in a state to start [current status: ' + ec2info[1] + ']')
         sys.exit(2)
      else:
         cmd = cmd + ' ' + ec2info[0]
   print("Starting: " + cmd)
   p = Popen(cmd, shell=True,
                stdout=PIPE,
                stderr=STDOUT)
   ec2lib.formatReturn(p.communicate()) # Display return values
elif args.Action == 'getip':
   if len(InstanceList) == 1:
      print(InstanceList[0][3]) 
   else:	  
      for ec2info in InstanceList:
         if ec2info[1] != 'stopped':
            ec2Name = '{:15.15}'.format(ec2info[2])
            print(ec2info[0] + ": (" + ec2Name + ') ' + ec2info[3])  
elif args.Action == 'reboot':
   cmd = 'aws ec2 reboot-instances --instance-ids'
   for ec2info in InstanceList:
      """
      if ec2info[1] != 'stopped':
         print(ec2info[0] + ' is not in a state to start [current status: ' + ec2info[1] + ']')
         sys.exit(2)
      else:
	  """
      cmd = cmd + ' ' + ec2info[0]
   print("rebooting: " + cmd)
   p = Popen(cmd, shell=True,
                stdout=PIPE,
                stderr=STDOUT)
   p.communicate() # Display return values
	  
	  
	  
	  
	  
	  
	  
	  