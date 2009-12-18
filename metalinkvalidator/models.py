from google.appengine.ext import db
#from urlparse import urlparse as urlp
#import os.path
#import re
#import logging

#A word, this is just left over from the project I branched this code of off
#class Word(db.Model):
#  hitcount = db.IntegerProperty(default = 0)
#  
#  def __str__(self):
#    return '%s (%i)' % (self.value(), self.hitcount)
#  
#  @staticmethod
#  def load_by_value(words):
#    #Return the given string words as Word entities, loaded from the database if possible
#    loaded = Word.get_by_key_name(words)
#    for i in xrange(len(loaded)):
#      if loaded[i] == None:
#        loaded[i] = Word(key_name = '%s' % words[i])
#        loaded[i].put()
#    return loaded
#  
#  #get_by_id()
#  def value(self):
#    return self.key().name()

