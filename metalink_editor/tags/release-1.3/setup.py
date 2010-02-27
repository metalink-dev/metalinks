# setup.py
from distutils.core import setup
import sys
import zipfile
import os
import shutil

APP_NAME = 'Metalink Editor'
VERSION = '1.3'
LICENSE = 'GPL'
DESC = ''
AUTHOR_NAME = 'Hampus Wessman'
EMAIL = ''
URL = 'http://hampus.vox.nu/metalink/'

scripts = ["meditor.py"]
data = ["metalink_small.png", "metalink_small.ico", "metalink.png", "license.txt", "changelog.txt", "readme.txt"]

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity
    version="0.0.0.1"
    processorArchitecture="x86"
    name="Controls"
    type="win32"
/>
<description>Metalink editor</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
"""

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
    
def clean():
    #ignore = ["NSIS\\gnupg-w32cli-1.4.9.exe"]
    
    filelist = ["MANIFEST"]
    filelist.extend(rec_search(".exe"))
    filelist.extend(rec_search(".zip"))
    filelist.extend(rec_search(".pyc"))
    filelist.extend(rec_search(".pyo"))
    
    try:
        shutil.rmtree("build")
    except WindowsError: pass
    try:
        shutil.rmtree("dist")
    except WindowsError: pass
    try:
        shutil.rmtree("files")
    except WindowsError: pass
    
    for filename in filelist:
        #if filename not in ignore:
            try:
                os.remove(filename)
            except WindowsError: pass

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

if sys.argv[1] == 'py2exe':
    import py2exe
    setup(
        windows = [
            {
                "script": "metalink_editor.py",
                "icon_resources": [(1, "metalink.ico")],
                "other_resources": [(24,1,manifest)]
            },
        ],
        console = ["meditor.py"],
        data_files=[('', ["metalink_small.png", "metalink_small.ico", "metalink.png", "license.txt", "changelog.txt", "readme.txt"])],
        name = APP_NAME,
        version = VERSION,
        license = LICENSE,
        description = DESC,
        author = AUTHOR_NAME,
        author_email = EMAIL,
        url = URL        
    )

elif sys.argv[1] == 'clean':
    clean()

elif sys.argv[1] == 'zip':
    #print "Zipping up..."
    create_zip("dist/", APP_NAME + "-" + VERSION + "-win32.zip")

elif sys.argv[1] == 'install':
    setup(scripts = scripts,
	#packages = packages,
        data_files=[('', data)],
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )

    if os.name == 'posix':
        for filename in scripts:
            mypath = "/usr/bin/"
            try:
                os.symlink(mypath + filename, mypath + filename[:-3])
                print "linking " + mypath + filename + " -> " + mypath + filename[:-3]
            except OSError: pass
            
if sys.argv[1] == 'sdist':
    setup(scripts = scripts,
	#packages = packages,
      data_files = [('', data)],
      name = APP_NAME,
      version = VERSION,
      license = LICENSE,
      description = DESC,
      author = AUTHOR_NAME,
      author_email = EMAIL,
      url = URL
      )

