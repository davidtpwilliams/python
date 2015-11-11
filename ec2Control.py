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
    #print(line)
    myjson = myjson + line
   
myj = json.loads(myjson)  

# Examine the returned ec2 descriptions for name, status, and Tags:Name,Value
count = 0
InstanceId = ""
Status = ""
InstanceDict = dict()
for i in myj['Reservations']:
   InstanceId = myj['Reservations'][count]['Instances'][0]['InstanceId']
   Status = myj['Reservations'][count]['Instances'][0]['State']['Name']
   for tag in myj['Reservations'][count]['Instances'][0]['Tags']:
      if (tag['Key'] == 'Name'):
         NameTag = tag['Value']
   ec2lib.addInstance(InstanceId, Status, InstanceDict, NameTag)
   count = count + 1

   
# Process AWS CLI calls ---------------------------------------   
# Start, stop depending on status or get instance id and status
if args.Action == 'status':
   for key in InstanceDict:
      print ("Instance: " + key + " " + ec2lib.printStatusName(InstanceDict[key]))
elif args.Action == 'stop':
   cmd = 'aws ec2 stop-instances --instance-ids'
   for key in InstanceDict:
      if ec2lib.extractStatus(InstanceDict[key]) != 'running':
         print(key + ' is not in a state to stop')
      else:
         cmd = cmd + ' ' + key	 
   print("Stopping: " + cmd)
   p = Popen(cmd, shell=True,
                 stdout=PIPE,
                 stderr=STDOUT)
   print(p.communicate())  # Display return values
elif args.Action == 'start':
   cmd = 'aws ec2 start-instances --instance-ids'
   for key in InstanceDict:
      if ec2lib.extractStatus(InstanceDict[key]) != 'stopped':
         print(key + ' is not in a state to start')
      else:
         cmd = cmd + ' ' + key
   print("Starting: " + cmd)
   p = Popen(cmd, shell=True,
                stdout=PIPE,
                stderr=STDOUT)
   print(p.communicate()) # Display return values
   
	  
	  
	  
	  
	  
	  
	  
	  
	  