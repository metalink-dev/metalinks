# -*- coding: utf-8 -*-

from distutils.core import setup
import sys
import os.path
import shutil
import glob
import zipfile

APP_NAME = 'GGet'
VERSION = '0.0.4'
LICENSE = 'GPL'
DESC = ''
AUTHOR_NAME = 'Neil McNab'
EMAIL = 'webmaster@nabber.org'
URL = 'http://www.nabber.org/projects/'


def clean():
    ignore = []
    
    filelist = []
    #filelist.extend(glob.glob("*metalink*.txt"))
    filelist.extend(rec_search(".exe"))
    filelist.extend(rec_search(".zip"))
    filelist.extend(rec_search(".pyc"))
    filelist.extend(rec_search(".pyo"))
    filelist.extend(rec_search(".mo"))
    filelist.extend(rec_search(".pot"))
    
    try:
        shutil.rmtree("build")
    except: pass
    try:
        shutil.rmtree("dist")
    except: pass
    # try:
        # shutil.rmtree("buildMetalink")
    # except: pass
    # try:
        # shutil.rmtree("buildmetalinkw")
    # except: pass
    
    try:
        shutil.rmtree("tests_temp")
    except: pass
    
    for filename in filelist:
        if filename not in ignore:
            try:
                os.remove(filename)
            except: pass

def create_zip(rootpath, zipname, mode="w"):
    print zipname
    myzip = zipfile.ZipFile(zipname, mode, zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(rootpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            filehandle = open(filepath, "rb")
            filepath = filepath[len(rootpath):]
            text = filehandle.read()
            #print filepath, len(text)
            myzip.writestr(filepath, text)
            filehandle.close()
    myzip.close()

def localegen():
    localedir = "locale"
    ignore = ("setup.py", "test.py")

    files = rec_search(".py")
    for pyfile in files:
        if os.path.basename(pyfile) not in ignore:
            potdir = os.path.join(os.path.dirname(pyfile), localedir, os.path.basename(pyfile))[:-3]
            print potdir
            try:
                os.makedirs(os.path.join(os.path.dirname(pyfile), localedir))
            except: pass

            command = os.path.join(sys.prefix, "Tools/i18n/pygettext.py") + " --no-location -d \"%s\" \"%s\"" % (potdir, pyfile)
            print(command)
            result = os.system(command)
            if result != 0:
                raise AssertionError, "Generation of .pot file failed for %s." % pyfile


def localecompile():
    files = rec_search(".po")

    for pofile in files:
        command = os.path.join(sys.prefix, "Tools/i18n/msgfmt.py") + " \"%s\"" % pofile
        print(command)
        result = os.system(command)
        if result != 0:
            raise AssertionError, "Generation of .mo file failed for %s." % pofile
            
def rec_search(end, abspath = True):
    start = os.path.dirname(__file__)
    mylist = []
    for root, dirs, files in os.walk(start):
        for filename in files:
            if filename.endswith(end):
                if abspath:
                    mylist.append(os.path.join(root, filename))
                else:
                    mylist.append(os.path.join(root[len(start):], filename))
                    
    return mylist

if sys.argv[1] == 'sdist':
    scripts = rec_search(".py")

    localegen()

    setup(scripts = scripts,
	#packages = packages,
      #data_files = data,
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )

elif sys.argv[1] == 'translate':
    localegen()
    localecompile()

elif sys.argv[1] == 'clean':
    clean()

elif sys.argv[1] == 'py2exe':
    import py2exe

    #localegen()
    #localecompile()
    
    setup(windows = ["gget.py"],
      #  zipfile = None,
      options={"py2exe" : {"packages": 'encodings', "includes" : "cairo, pango, pangocairo, atk, gobject", "optimize": 2}},
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )

elif sys.argv[1] == 'zip':
    #print "Zipping up..."
    create_zip("dist/", APP_NAME + "-" + VERSION + "-win32.zip")
