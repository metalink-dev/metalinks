#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

