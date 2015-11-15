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

# Add instance details to list.	  
def addInstance(ID, Status, NameTag, PublicIp, InstanceList):		
   list = [ID, Status, NameTag, PublicIp]
   InstanceList.append(list)
   
# Format instance name and status to make it look neater.   
def printec2Info(ec2Info):
   TagName = '{:15.15}'.format(ec2Info[2])
   print ('Instance: ' + ec2Info[0] + " (" + TagName + ") " + ec2Info[1] + " (I.P.) " + ec2Info[3])	
   
def formatReturn(byteFormat):
   returnStr = str(byteFormat)
   replaceMe = dict()
   replaceMe = {"[\\r\\n":"","{\\r\\n":"", "(b'":"", "\\r\\n":"", "{":"", "[":"","]":"", "}":"", ")":"", " ":"", ",":"\n", "None":""}
   for textRemove, space in replaceMe.items():
      returnStr = returnStr.replace(textRemove, space)
   print("\nReturn Value:\n" + returnStr)