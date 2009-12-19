#!/usr/bin/env python
from google.appengine.ext import webapp, db
import os
from google.appengine.ext.webapp import template

class TemplateRenderer:
  '''Add member to easily use templates'''
  def write_template(self, templateName, values):
    path = os.path.join(os.path.dirname(__file__), 'templates', templateName)
    self.response.out.write(template.render(path, values))
    return

class Home(webapp.RequestHandler, TemplateRenderer):
  def head(self):
    return
  def get(self):
    self.write_template('index.html', {'body': 'This page is currently under construction by the <a href="http://sourceforge.net/apps/trac/metalinks/">Metalinks project</a>.'})


class RobotsTXT(webapp.RequestHandler):
  def head(self):
    return
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'  
    self.response.out.write('# 200 OK')

