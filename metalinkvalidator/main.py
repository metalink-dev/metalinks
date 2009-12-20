#!/usr/bin/env python2.5
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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import views
import logging

application = webapp.WSGIApplication(
                                     [
                                      ('/', views.Home),
                                      ('/validate', views.Validator),
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
