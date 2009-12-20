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

      #Handle response status
      if page.content_was_truncated:
        v.addError('The content of the download was truncated, it may be to large. Check the size or try again later.')
      if page.status_code != 200:
        v.addError('The status code of the page was not 200 (it was %i instead)' % page.status_code, fatal = True)
      #We skip page.final_url currently
      if hasattr(page, 'final_url'):
        v.addInfo('Final url was: %s' % page.final_url)
      
      #Load content into validator
      v.setContent(page.content)
      v.run()
    except google.appengine.api.urlfetch.InvalidURLError, e:
      v.addError('Invalid url, "%s" is not considered valid' % url, fatal = True)
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

