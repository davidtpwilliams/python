import sys
import re

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

# Add instance info to dictionary.	  
def addInstance(ID, Status, InstanceDict, NameTag):
    if ID in InstanceDict:
        print ('error')
    else:
        InstanceDict[ID] = NameTag + " => " + Status

# The status and tag:Name value are stored as one string (Name => Status)
# This function will extract the status part
def extractStatus (StatusName):
   seperator = "=> "
   idx = StatusName.find(seperator)
   status = StatusName[idx+3:]
   print ("Status = " + status)
   return status
   
def printStatusName(StatusName):
   seperator = "=> "
   idx = StatusName.find(seperator)
   status = StatusName[idx+3:]
   name = '{:15.15}'.format(StatusName[:idx])
   #print(name + status)
   #print ('{}' + ' => ' + '{}'.format(name, status))
   return '(' + name + ')' + ' => ' + status