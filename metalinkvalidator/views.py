#!/usr/bin/env python
from google.appengine.ext import webapp, db
import os
from google.appengine.ext.webapp import template
import google.appengine.api.urlfetch
import validator

class TemplateRenderer:
  '''Add member to easily use templates'''
  def write_template(self, templateName, values = None):
    if not values:
      values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates', templateName)
    self.response.out.write(template.render(path, values))
    return

class Validator(webapp.RequestHandler, TemplateRenderer):
  def head(self):
    return
  def get(self):
    #Fetch body
    url = self.request.get("url")
    v = validator.Validator()
    try:
      page = google.appengine.api.urlfetch.fetch(url)
      #TODO: handle response values and status codes: http://code.google.com/appengine/docs/python/urlfetch/responseobjects.html
      v.setContent(page.content)
      v.run()
    except google.appengine.api.urlfetch.InvalidURLError, e:
      v.messages += ['Invalid url given, we got %s' % url]
    self.write_template('validation_result.html', {'validator': v})



class Home(webapp.RequestHandler, TemplateRenderer):
  def head(self):
    return
  def get(self):
    self.write_template('index.html')


class RobotsTXT(webapp.RequestHandler):
  def head(self):
    return
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'  
    self.response.out.write('# 200 OK')

