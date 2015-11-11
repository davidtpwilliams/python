#!c:/Python34/python.exe -u 
import sys
import subprocess
import os, errno
import myssl
   
putty = "C:\\Users\\User\\Desktop\\Work\putty.exe"
print("\tPress ENTER for defaults")
profile = input('\tEnter the putty profile you want to use [AWSWebServer]: ')
if len(profile) == 0:
   profile = 'AWSWebServer'

keyfile = input('\tEnter the key file name to use [awscert]:')
if len(keyfile) == 0:
   keyfile = 'awscert'

password = " "

#Unlock key file .lck and keep password for encryption
password = myssl.unlock(keyfile)

#SSH to AWS using Putty profile
command = "%s -load %s" % (putty, profile)
p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)	
#output, error = p.communicate()	   

#Lock the key file .ppk
myssl.lock(keyfile, password)
exit(0)