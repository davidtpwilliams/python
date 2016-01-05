import datetime
class Logging(object):
   def __init__(self, filename):
      self.filename = filename
      self.logdate = datetime.datetime.now().strftime("%A %d %B %Y - %I:%M%p")
      self.logfile = open(self.filename, 'a')
      self.logfile.write("----------------------------------\n")
      self.logfile.write(self.logdate + "\n")
		
   def logit(self, Message, Screen):
      self.logfile.write(Message + '\n')
      if Screen:
         print(Message)
