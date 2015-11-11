# python
python scripts

Note: .ppk files are converted .pem files

myssl.py => module contains two functions lock and unlock.  Using openssl a file is either en-crypted or de-crypted. Use
            specifically to lock AWS keys.

keylock.py => manually lock/unlock any file in the ../keys/ directory with .lck or .ppk extension

sshaws.py => unlock awscert.lck => awscert.ppk, ssh to AWS then lock awscert.ppk => awscert.lck

The ec2lib.py contains functions for use in ec2Control.py

ec2Control.py will stop, start and get the status of EC2 instances.  The requests can be filtered on Tags Name:Value
