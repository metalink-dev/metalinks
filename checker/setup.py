# -*- coding: utf-8 -*-

from distutils.core import setup
import sys
import os.path
import shutil
import glob
import zipfile

APP_NAME = 'metalink-checker'
VERSION = '5.1'
LICENSE = 'GPL'
DESC = 'A metalink checker and download client.'
AUTHOR_NAME = 'Neil McNab'
EMAIL = 'neil@nabber.org'
URL = 'http://www.nabber.org/projects/'

#main is first
modules = ['console', 'metalink', 'GPG', 'download', 'checker']
outputfile = "metalinkc.py"

readhandle = open("README.txt")
header = readhandle.read()
readhandle.close()

def merge(header, modules, outputfile):
    modules.reverse()
    modulelist = []
    imports = []
    redef = {}

    for module in modules:
        imports.extend(readfile(module, True, modules))

        exec("import " + module)
        moduleobj = eval(module)
        listing = dir(moduleobj)
        for stritem in listing:
            item = getattr(moduleobj, stritem)

            if not stritem.startswith("__") and type(item) != type(sys):
                try:
                    redef[module] += module + "." + stritem + " = " + stritem + "\n"
                except KeyError:
                    redef[module] = module + "." + stritem + " = " + stritem + "\n"

    writehandle = open(outputfile, "w")
    writehandle.write(header)

    importdict = {}
    newimports = []
    for importline in imports:
        if importline.startswith("import "):
            importdict[importline] = 1
        else:
            newimports.append(importline)
    newimports.extend(importdict.keys())
    imports = newimports
    #    writehandle.write(importline + "\n")
    writehandle.writelines(imports)
    writehandle.write("class Dummy:\n    pass\n")
    
    for modulename in modules:
        filelist = readfile(modulename)
        writehandle.writelines(filelist)
        writehandle.write(modulename + " = Dummy()\n" + redef[modulename])
        
    writehandle.close()
    return

def readfile(modulename, imports=False, ignore=[]):
    filelist = []
    prevline = ""
    filehandle = open(modulename + ".py")
    line = filehandle.readline()
    while line:
        if line.strip().startswith("import "):
            if imports and line.strip()[7:] not in ignore:
                filelist.append(line.strip(" \t"))
        elif prevline.strip().startswith("try: import "):
            if imports and prevline.strip()[11:] not in ignore:
                filelist.append(prevline.strip(" \t"))
                filelist.append(line.strip(" \t"))
        elif not imports and not line.strip().startswith("try: import "):
            filelist.append(line)
        prevline = line
        line = filehandle.readline()
    filehandle.close()
    return filelist

def clean():
    ignore = []
    
    filelist = []
    filelist.extend(glob.glob("*metalink*.txt"))
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
    try:
        shutil.rmtree("buildMetalink")
    except: pass
    try:
        shutil.rmtree("buildmetalinkw")
    except: pass
    
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

elif sys.argv[1] == 'merge':
    merge(header, modules, outputfile)

elif sys.argv[1] == 'translate':
    localegen()
    localecompile()

elif sys.argv[1] == 'clean':
    clean()

elif sys.argv[1] == 'py2exe':
    merge(header, modules, outputfile)
        
    import py2exe

    #localegen()
    #localecompile()
    
    setup(console = ["metalinkc.py"],
        zipfile = None,
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )
    setup(windows = ["guitk.py"],
        zipfile = None,
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
