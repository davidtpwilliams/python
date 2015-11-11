#!c:/Python34/python.exe -u 
import sys
import myssl

#Check arguments
if (len(sys.argv) != 3) or (sys.argv[1] != '-l' and sys.argv[1] != '-u'):
   print("Usage: " + sys.argv[0] + " -[l|u] filename")
   exit(1)

#Run unlock or lock
filename = sys.argv[2]
if sys.argv[1] == '-l':
   myssl.lock(filename, "")
elif sys.argv[1] == '-u':
   myssl.unlock(filename)
else:
   print("We should not be here")