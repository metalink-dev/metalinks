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

            if not stritem.startswith("__"):
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

merge(header, modules, outputfile)
