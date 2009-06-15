@ECHO OFF

set BUILD_DIR=build
set APPNAME=DLApplet

call sample_setenv.bat
call setenv.bat

echo Cleaning up old files...
call %JYTHON_HOME%\jython.bat setup.py clean

mkdir %BUILD_DIR%

cd jyinterface
%JAVA_HOME%\bin\javac.exe -Xlint:unchecked -classpath %JYTHON_HOME%\jython.jar Download.java Downloader.java JythonFactory.java ProgressRenderer.java DownloadTableModel.java DownloadManager.java DLApplet.java
mkdir ..\%BUILD_DIR%\jyinterface
move *.class ..\%BUILD_DIR%\jyinterface
cd ..
cd %BUILD_DIR%

:: If opt parameter is specified, use optimized mode
IF "%1"=="opt" GOTO opt

:quick
echo Doing a quick build... (for a distributable build you should use the "opt" option to optimize)
xcopy /S /I /Q %JYTHON_HOME%\Lib\* .

copy %JYTHON_HOME%\jython.jar .

GOTO jar

:jar

cd ..

copy JDownload.py %BUILD_DIR%\.
copy JDownloader.py %BUILD_DIR%\.
copy download.py %BUILD_DIR%\.
copy xmlutils.py %BUILD_DIR%\.

echo Compressing into jar files...

cd %BUILD_DIR%

echo Class-Path: jython.jar > manifest.txt
%JAVA_HOME%\bin\jar.exe cfme0 %APPNAME%.jar manifest.txt jyinterface.DownloadManager jyinterface xml/*.py xml/parsers/*.py encodings/*.py *.py

echo Signing applet...

%JAVA_HOME%\bin\jarsigner.exe %APPNAME%.jar %APPNAME%
%JAVA_HOME%\bin\jarsigner.exe jython.jar %APPNAME%

IF "%1"=="" GOTO end

echo Recompressing...

for %%F in (jython DLApplet) do (
%ZIP% x -tzip %%F.jar -otemp
cd temp
%ZIP% a -tzip -mx=9 ../%%F.jar *
cd ..
rmdir /S /Q temp
)

GOTO end

:opt
echo Repackaging jython with only needed classes...
mkdir jython
cd jython
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar com/sun
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/antlr
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/apache/xerces
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/compiler
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/constantine
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/core
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/expose
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/modules
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/objectweb
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/posix
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/util
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/Version.class
%JAVA_HOME%\bin\jar.exe xf %JYTHON_HOME%\jython.jar org/python/version.properties

%JAVA_HOME%\bin\jar.exe cf0 jython.jar *
move jython.jar ..\.
cd ..

:: import standard .py files

echo Doing an optimized .py build...
REM copy %JYTHON_HOME%\Lib\* %BUILD_DIR%\.
copy %JYTHON_HOME%\Lib\urllib2.py .
REM copy %JYTHON_HOME%\Lib\thread.py %BUILD_DIR%\.
copy %JYTHON_HOME%\Lib\socket.py .
copy %JYTHON_HOME%\Lib\os.py .
copy %JYTHON_HOME%\Lib\md5.py .
copy %JYTHON_HOME%\Lib\sha.py .
copy %JYTHON_HOME%\Lib\re.py .
copy %JYTHON_HOME%\Lib\math.py .
copy %JYTHON_HOME%\Lib\time.py .
copy %JYTHON_HOME%\Lib\urlparse.py .
copy %JYTHON_HOME%\Lib\hashlib.py .
copy %JYTHON_HOME%\Lib\locale.py .
copy %JYTHON_HOME%\Lib\threading.py .
copy %JYTHON_HOME%\Lib\ftplib.py .
copy %JYTHON_HOME%\Lib\httplib.py .
copy %JYTHON_HOME%\Lib\base64.py .
copy %JYTHON_HOME%\Lib\sys.py .
copy %JYTHON_HOME%\Lib\gettext.py .

copy %JYTHON_HOME%\Lib\__future__.py .
copy %JYTHON_HOME%\Lib\string.py .
copy %JYTHON_HOME%\Lib\sre_compile.py .
copy %JYTHON_HOME%\Lib\sre_constants.py .
copy %JYTHON_HOME%\Lib\sre_parse.py .
copy %JYTHON_HOME%\Lib\copy_reg.py .
copy %JYTHON_HOME%\Lib\types.py .
copy %JYTHON_HOME%\Lib\weakref.py .
copy %JYTHON_HOME%\Lib\UserDict.py .
copy %JYTHON_HOME%\Lib\traceback.py .
copy %JYTHON_HOME%\Lib\linecache.py .
copy %JYTHON_HOME%\Lib\stat.py .
copy %JYTHON_HOME%\Lib\ntpath.py .
copy %JYTHON_HOME%\Lib\nturl2path.py .
copy %JYTHON_HOME%\Lib\atexit.py .
copy %JYTHON_HOME%\Lib\mimetools.py .
copy %JYTHON_HOME%\Lib\rfc822.py .
copy %JYTHON_HOME%\Lib\tempfile.py .
copy %JYTHON_HOME%\Lib\random.py .
copy %JYTHON_HOME%\Lib\warnings.py .
copy %JYTHON_HOME%\Lib\posixpath.py .
copy %JYTHON_HOME%\Lib\bisect.py .
copy %JYTHON_HOME%\Lib\urllib.py .
copy %JYTHON_HOME%\Lib\codecs.py .
copy %JYTHON_HOME%\Lib\gzip.py .
copy %JYTHON_HOME%\Lib\zlib.py .
copy %JYTHON_HOME%\Lib\StringIO.py .
copy %JYTHON_HOME%\Lib\copy.py .
copy %JYTHON_HOME%\Lib\BaseHTTPServer.py .
copy %JYTHON_HOME%\Lib\SocketServer.py .

xcopy /S /I /Q %JYTHON_HOME%\Lib\xml xml
xcopy /S /I /Q %JYTHON_HOME%\Lib\encodings encodings

GOTO jar

:end

cd ..