
import sys
import getpass
import subprocess
import os, errno
import time

#Declare variables 
keydir = "C:\\Users\\User\\Desktop\\Work\\Keys"
openssl = "C:\\Openssl\\openssl.exe"
snooze = 5

# An encrypted AWS key is decrypted - unlocked with the password used to encrypt
def unlock(key_file):
   #Declare variables
   awscert = keydir + "\\" + key_file

   #first check if files are available
   if not os.path.exists(openssl):
      print ("\tERROR: Cannot access openssl.exe from %s, exiting" % (openssl))
      exit(1) 

   if os.path.exists(awscert + ".ppk"):
      print("\tWARNING: The file %s already exists" % (awscert + ".ppk"))
	  # Just return as the file is already unlocked
      return ""
	  
   if not os.path.exists(awscert + ".lck"):
      print("\tERROR: The file %s does not exist, \nexiting program." % (awscert + ".lck"))
      exit(1)
	  
   #Ask for password
   pswd = getpass.getpass('\tTo de-crypt enter Password:')

   #Un-encrypt encrypted.ppk
   command = "%s enc -in %s.lck -out %s.ppk -d -aes256 -pass pass:%s" % (openssl, awscert, awscert, pswd)

   try:
      p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   except OSError:
      print('\tERROR: Well darn.')
   
   #Sleep for some seconds then remove .ppk file.
   time.sleep(snooze)   
   #Check that the encryption worked before removing file.
   if os.path.exists(awscert + ".ppk"):
      os.remove(awscert + ".lck")
   else:
      print("\tERROR: Sorry, I can not remove %s.lck file." % awscert)
   print("\tUnlocked " + key_file + " successfully")
   return pswd   #Return password for lock call.

# Lock the AWS key using a password already given or one provided through stdin   
def lock(key_file, password):
   awscert = keydir + "\\" + key_file
   
   #first check if files are available
   if not os.path.exists(openssl):
      print ("\tERROR: Cannot access openssl.exe from %s, exiting" % (openssl))
      exit(1) 

   if not os.path.exists(awscert + ".ppk"):
      print("\tERROR: The file %s does not exist, \nexiting program" % (awscert + ".ppk"))
      exit(1)
	  
   #Ask for password if called alone else use existing
   if (len(password) > 5):
      pswd = password
   else:
      pswd = getpass.getpass('\tTo en-crypt Password:')

   #Encrypt encrypted.ppk
   command = "%s enc -in %s.ppk -out %s.lck -e -aes256 -pass pass:%s" % (openssl, awscert, awscert, pswd)

   try:
      p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   except OSError:
      print('\tERROR: Well darn.')
	  
   #Sleep for some seconds to give ssh time to use the key fsthen remove .ppk file.
   time.sleep(snooze)   
   
   #Check that the encryption worked before removing file.
   if os.path.exists(awscert + ".lck"):
      os.remove(awscert + ".ppk")
   else:
      print("\tERROR: Sorry, I can not remove %s.ppk file." % awscert)
   print("\tLocked " + key_file + " successfully")
   return 0