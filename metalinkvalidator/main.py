#!/usr/bin/env python2.5
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import views
import logging

application = webapp.WSGIApplication(
                                     [
                                      #('/', views.Home), <- dynamic homepage is still a todo ;)
                                      ('/robots.txt', views.RobotsTXT),
                                     ],
                                     debug = True)

def main():
  #logging.getLogger().setLevel(logging.DEBUG)
  logging.getLogger().setLevel(logging.ERROR)
  run_wsgi_app(application)

def profile_main():
 # This is the main function for profiling 
 import cProfile, pstats, StringIO
 import logging
 prof = cProfile.Profile()
 prof = prof.runctx("main()", globals(), locals())
 stream = StringIO.StringIO()
 stats = pstats.Stats(prof, stream=stream)
 stats.sort_stats("time")  # Or cumulative
 stats.print_stats(80)  # 80 = how many to print
 # The rest is optional.
 # stats.print_callees()
 # stats.print_callers()
 logging.info("Profile data:\n%s", stream.getvalue())

if __name__ == "__main__":
  main()
