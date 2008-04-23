#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2008, Neil McNab
# License: GNU General Public License Version 2
#   (http://www.gnu.org/copyleft/gpl.html)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Filename: $URL$
# Last Updated: $Date$
# Version: $Rev$
# Author(s): Neil McNab
#
# Description:
#   Command line application that tests metalink clients.  Requires Python 2.5
# or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. Run on the command line using: python tester.py
#   3. The program you are testing needs to return failure codes on exit.
#
########################################################################

import os
import hashlib
import sys
import optparse
import time
import subprocess

# Metalink Checker
CMD = "\"" + sys.executable + "\" ../console.py -d -f %s"
# Aria2
# CMD = "\"c:\\program files\\aria2\\aria2c.exe\" -M %s"

OUTDIR = os.getcwd()
TIMEOUT = 600

IGNORE_TESTS = [] #["3_metalink-bad-piece1and2-without-torrent.metalink",
                #"3_metalink-bad-piece2-without-torrent.metalink"]

FILELIST = [
    {"filename": "curl-7.18.1.tar.bz2",
    "size": 1700966,
    "checksums": {"sha1": "685b9388ee9e646158a83cd435f7be664816ad78"}},
    {"filename": "curl-7.18.1.tar.gz",
    "size": 2225578,
    "checksums": {"sha1": "5d72f9fbf3eab6474a8dc22192056119030087f6"}},
    {"filename": "curl-7.18.1.zip",
    "size": 2787188,
    "checksums": {"sha1": "87de05976acb909c7edbed8ba0935f0a51332195"}},
    {"filename": "OOo_2.3.1_Win32Intel_install_en-US.exe",
    "size": 112341981,
    "checksums": {"sha1": "2c2849d173b1a5e6f8a3dc986383ee897bf4364d"}}
]

def run_tests(level=3):
    filedir = "./"
    filenames = os.listdir(filedir)
    filenames.sort()

    summary = {}

    for filename in filenames:
        if filename.endswith(".metalink") and filename not in IGNORE_TESTS:
            mysplit = filename.split("_")
            if IsInt(mysplit[0]):
                if int(mysplit[0]) <= level:
                    summary[filename] = run_test(filename)
                    print "-" * 79

    clean()

    levels = {}
    totallevels = {}

    print "PASS\tTest File Name"
    print "===================="
    templist = summary.keys()
    templist.sort()
    for item in templist:
        print "%s: %s" % (summary[item], item)
        mysplit = item.split("_")
        if IsInt(mysplit[0]):
            num = int(mysplit[0])
            try:
                totallevels[num] += 1
            except KeyError:
                totallevels[num] = 1
            if summary[item]:
                try:
                    levels[num] += 1
                except KeyError:
                    levels[num] = 1

    templist = totallevels.keys()
    templist.sort()
    for i in templist:
        result = "FAIL"
        if levels[i] == totallevels[i]:
            result = "PASS"
        print "Level %s: %s (%s/%s)" % (i, result, levels[i], totallevels[i])

def run_test(filename):
        clean()
        subdir = "."
        if filename.find("subdir") != -1:
            subdir = "curl"
            
        print "Running:", filename

        #print CMD % filename
        try:
            retcode = system(CMD % filename, TIMEOUT)
        except AssertionError:
            print "FAIL: Test timed out"
            return False
        
        if retcode != 0:
            print "Program exited with error code: %s" % retcode
            if filename.find("fail") != -1:
                print "PASS"
                return True
            else:
                print "FAIL: Error code returned"
                return False

        checklist = [0]
        if filename.find("three") != -1:
            checklist = [0,1,2]
        elif filename.startswith("4"):
            checklist = [3]
            
        for checkindex in checklist:
            temp = FILELIST[checkindex]
            tempname = os.path.join(OUTDIR, subdir, temp["filename"])
            if not os.access(tempname, os.F_OK):
                print "FAIL: File does not exist", tempname
                return False
            elif os.stat(tempname).st_size != temp["size"]:
                print "FAIL: Wrong file size", tempname
                return False
            elif filehash(tempname, hashlib.sha1()) != temp["checksums"]["sha1"]:
                print "FAIL: Bad file checksum", tempname
                return False
            
        print "PASS"
        return True

def clean():
    print "Running cleanup..."
    for fileitem in FILELIST:
        try:
            os.remove(os.path.join(OUTDIR, fileitem["filename"]))
        except: pass
        try:
            os.remove(os.path.join(OUTDIR, "curl", fileitem["filename"]))
        except: pass


def filehash(thisfile, filesha):
    '''
    First parameter, filename
    Returns SHA1 sum as a string of hex digits
    '''
    try:
        filehandle = open(thisfile, "rb")
    except:
        return ""

    data = filehandle.read()
    while(data != ""):
        filesha.update(data)
        data = filehandle.read()

    filehandle.close()
    return filesha.hexdigest()

def IsInt(str):
	""" Is the given string an integer?	"""
	ok = True
	try:
		num = int(str)
	except ValueError:
		ok = False
	return ok

def system(command, timeout=600, cwd=None):
    '''
    Alternative to os.system(), adds optional parameter to kill process
    after a given amount of time.
    First parameter, command to run on the local system
    Second parameter, optional, timeout command after this many seconds
    cwd string working directory or None
    Returns command exit code
    '''
    endtime = time.time() + timeout

    print command
    process = subprocess.Popen(command, shell=True, env=os.environ, cwd=cwd)
    while(True):
        time.sleep(1)
        #print "check:", process.poll()
        if process.poll() != None:
            return process.poll()
        if endtime <= time.time():
            # kill process here
            if os.name == 'nt':
                command = "taskkill /F /PID %s /T" % process.pid
            else:
                command = "kill -9 %s" % process.pid
            os.system(command)
            #print "Test timed out.  Process killed."
            raise AssertionError
            #return process.poll()

def run():
    '''
    Start a console version of this application.
    '''
    global OUTDIR, CMD, TIMEOUT
    # Command line parser options.
    parser = optparse.OptionParser()
    parser.add_option("--level", "-l", dest="level", help="Set the level to test up to (default: 3)")
    parser.add_option("--command", "-c", dest="command", help="Command to run (use quotes as needed), %%s=metalink file")
    parser.add_option("--outdir", "-o", dest="outdir", help="Directory where the metalink client will output the downloaded files")
    parser.add_option("--timeout", "-t", dest="timeout", help="Sets the amount of time a test can run until it times out (default: 600 s)")
    parser.add_option("--testcase", "-f", dest="testcase", help="Run a single test case")
    (options, args) = parser.parse_args()

    if options.outdir != None:
        OUTDIR = options.outdir
    if options.command != None:
        CMD = options.command
    if options.timeout != None:
        TIMEOUT = int(options.timeout)

    if options.testcase != None:
        run_test(options.testcase)
        return

    if options.level != None:
        run_tests(options.level)
    else:
        run_tests(3)

if __name__=="__main__":
    run()
