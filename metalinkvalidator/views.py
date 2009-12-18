#!/usr/bin/env python
from google.appengine.ext import webapp, db
#from models import ....

class RobotsTXT(webapp.RequestHandler):
  def head(self):
    return
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'  
    self.response.out.write('# 200 OK')

