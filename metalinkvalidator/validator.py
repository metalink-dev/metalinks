
#This class should be kept independent of Google App engine, so using the url fetch service should be done outside of this file

class Message:
  def __init__(self, catagory, msg):
    self.catagory = catagory
    self.msg = msg
  
  def catagoryName(self):
    return self.catagory[0:1].upper() + self.catagory[1:]
  
  def __str__(self):
    return self.msg

'''Validate the given metalink content, collecting as much warnings and messages as possible'''
class Validator:

  def __init__(self):
    self.messages = []
    self.passed = False
    self.content = ''
  
  def setContent(self, content):
    self.content = content
  
  def addError(self, msg, fatal = False):
    '''Simple wrapper function to add an error message'''
    if fatal:
      self.passed = False
    self.messages.append(Message('error', msg))

  def addWarning(self, msg):
    '''Simple wrapper function to add a warning message'''
    self.messages.append(Message('warning', msg))
  
  def addInfo(self, msg):
    '''Simple wrapper function to add an info message'''
    self.messages.append(Message('info', msg))

  def statistics(self):
    '''Count the number of messages per catagory'''
    stats = {}
    for msg in self.messages:
      stats[msg.catagory] = stats.set_default(msg.catagory, 0) + 1
    return stats
  
  def run(self):
    self.messages.append(Message('info', 'Content length: %i' % len(self.content)))
    #Start with normal XML validation
    #Insert more checks here
    #Set self.passed if this validation ran successfully
    pass
