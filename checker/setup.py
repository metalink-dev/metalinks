import sys
import os.path

#main is first
modules = ['console', 'xmlutils', 'download', 'checker']
outputfile = "metalink.py"

readhandle = open("header.txt")
header = readhandle.read()
readhandle.close()

def merge(header, modules, outputfile):
    modules.reverse()
    modulelist = []
    imports = ""
    redef = {}

    for module in modules:
        imports += readfile(module, True)

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
    
    writehandle.write(imports + "class Dummy:\n    pass\n")
    
    for modulename in modules:
        filestring = readfile(modulename)
        writehandle.write(filestring)
        writehandle.write(modulename + " = Dummy()\n" + redef[modulename])
        
    writehandle.close()
    return

def readfile(modulename, imports=False):
    filestring = ""
    filehandle = open(modulename + ".py")
    line = filehandle.readline()
    while line:
        if imports == line.strip().startswith("import "):
            filestring += line
        line = filehandle.readline()
    filehandle.close()
    return filestring

def clean():    
    filelist = []
    filelist.extend(rec_search(".pyc"))
    filelist.extend(rec_search(".pyo"))
    
    for filename in filelist:
        try:
            os.remove(filename)
        except WindowsError: pass

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

if sys.argv[1] == 'merge':
    merge(header, modules, outputfile)

elif sys.argv[1] == 'translate':
    localegen()
    localecompile()
