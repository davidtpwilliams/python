import sys
import re
import time
import datetime
import json
from subprocess import Popen, PIPE, STDOUT

# Functions to handle ec2 access and json manipulation
def checktags(Tags):
   # Argument check -----------------------------------------------------------------------
   # Check the tags.  There can be either none or several and they come in Name:Value pairs
   TagDict = []
   if len(Tags)% 2 != 0:
      print ("ERROR: Wrong number of Tag arguments; Name=>Value pairs")
      count = 0
      for i in Tags:
         if count % 2 != 0:
            print(i)
         else:
            print('\t' + i + "=>",end="")
         count = count + 1
      if count % 2 != 0:
         print(' ???????')
      print("Please enter correct parameters")
      sys.exit(2)
   else:
      TagDict = []
      # Add to dictionary
      return dict(Tags[i:i+2] for i in range(0, len(Tags), 2))

# Add instance details to list.	  
def addInstance(ID, Status, NameTag, PublicIp, InstanceList):		
   list = [ID, Status, NameTag, PublicIp]
   InstanceList.append(list)
   
# Format instance name and status to make it look neater.   
def printec2Info(ec2Info, LogObject):
   TagName = '{:15.15}'.format(ec2Info[2])
   LogObject.logit('Instance: ' + ec2Info[0] + " (" + TagName + ") " + ec2Info[1] + " (I.P.) " + ec2Info[3], True)   
   
def formatReturn(byteFormat):
   returnStr = str(byteFormat)
   replaceMe = dict()
   replaceMe = {"[\\r\\n":"","{\\r\\n":"", "(b'":"", "\\r\\n":"", "{":"", "[":"","]":"", "}":"", ")":"", " ":"", ",":"\n", "None":""}
   for textRemove, space in replaceMe.items():
      returnStr = returnStr.replace(textRemove, space)
   print("\nReturn Value:\n" + returnStr)
  
def UpdateInstanceList(InstanceList, myj):  
   count = 0
   InstanceId = ""
   Status = ""
   PublicIp = ""
   for i in myj['Reservations']:
      InstanceId = myj['Reservations'][count]['Instances'][0]['InstanceId']
      try:
         PublicIp = myj['Reservations'][count]['Instances'][0]['PublicIpAddress']
      except:
         PublicIp = 'NONE'
      Status = myj['Reservations'][count]['Instances'][0]['State']['Name']
      NameTag = "NO NAME TAG"
      for tag in myj['Reservations'][count]['Instances'][0]['Tags']:
         if (tag['Key'] == 'Name'):
            NameTag = tag['Value']
      addInstance(InstanceId, Status, NameTag, PublicIp, InstanceList)
      count = count + 1
	  
def RunCliCommand(cmd, PrintReturn):
   p = Popen(cmd, shell=True,
            stdout=PIPE,
            stderr=STDOUT)
   if PrintReturn:
      formatReturn(p.communicate()) # Display return values
   return p
   
def GetNewIpAddress(InstanceID):
   count = 0
   cmd = "aws ec2 describe-instances --instance-ids " + InstanceID
   while count < 5:
      print ("Waiting for Public IP ...")
      time.sleep(5)  # Delay for 5 seconds then try again, max 10 tries
      print(cmd)
      p = RunCliCommand(cmd, False)
      myjson = ""		#Convert io.BufferedReader, byte data to json				  
      for line in p.stdout:
         line = line.decode(encoding='utf-8')
         myjson = myjson + line 
      myj = json.loads(myjson)
      print(myj['Reservations'][0]['Instances'][0]['PublicIpAddress'])
      try:
         PublicIp = myj['Reservations'][0]['Instances'][0]['PublicIpAddress']
      except:
         PublicIp = 'NONE'	
      if (PublicIp == 'NONE'):
         count = count + 1
         print("NONE")
      else:
         count = 5
   print("Public IP: " + PublicIp)
   return PublicIp

	  
def UpdateRoute53(InstanceName, PublicIp, LogObject):
   # First search in conf file for URL Name mappings 
   f = open('ec2.cfg', 'r')
   TYPE = 'A'
   TTL = 10
   HostedZone = "Z3JXA5H29528CX"
   COMMENT = "Update of IP from cli call (ec2desk.py)"
   Found = False
   for line in f:
      if (line.split('=')[0] == InstanceName):
         Name = line.split('=')[0]
         URL = line.split('=')[1]
         print("Name:" + Name + " URL:" + URL)
         LogObject.logit("Found server in config file ec2.cfg Name:" + Name + " URL:" + URL, True)
         Found = True
         break

   if not Found:		 
      LogObject.logit("Cannot find server " + InstanceName + " in ec2.cfg\nUnable to update Route53 A record with new IP", True)
      sys.exit(0)

   # Contruct temporary json file	  
   target = open('route53.json', 'w')
   target.truncate()
   target.write("{\n")
   target.write("  \"Comment\": \"" + COMMENT + "\""",\n")
   target.write("  \"Changes\":[\n")
   target.write("  {\n")
   target.write("      \"Action\": \"UPSERT\",\n")
   target.write("      \"ResourceRecordSet\":{\n")
   target.write("         \"ResourceRecords\":[\n")
   target.write("           {\n")
   target.write("              \"Value\": \"" + PublicIp + "\"""\n")
   target.write("           }\n")
   target.write("       ],\n")
   target.write("       \"Name\": \"" + URL.strip() + "\""",\n")
   target.write("       \"Type\": \"" + TYPE + "\""",\n")
   target.write("       \"TTL\": " + str(TTL) + "\n""")
   target.write("       }\n")
   target.write("     }\n")
   target.write("  ]\n")
   target.write("}\n")
   target.close()
	  
   cmd = "aws route53 list-hosted-zones"
   p = RunCliCommand(cmd, True)  
   # Extract the hosted zone from the return

   # Update route53 A record - currently this must exist - next step will be to create if it does not exist	  
   cmd = "aws route53 change-resource-record-sets --hosted-zone-id " + HostedZone + " --change-batch file://\"route53.json\""
   p = RunCliCommand(cmd, True)	
   #ec2Log("aws route53 change-resource-record-sets --hosted-zone-id " + HostedZone + " --change-batch file://\"route53.json\"", False)
   LogObject.logit("aws route53 change-resource-record-sets --hosted-zone-id " + HostedZone + " --change-batch file://\"route53.json\"", False)
   
