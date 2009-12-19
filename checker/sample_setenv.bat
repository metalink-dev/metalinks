SET PYTHONDIR=c:\Python25
SET PYINSTALLERDIR=c:\pyinstaller_1.3\pyinstaller-1.3
SET JYTHON_HOME="c:\jython2.5.0"
REM SET JAVA_HOME="C:\Program Files\Java\jdk1.6.0_12"
SET JAVAPATH=%JAVA_HOME%\bin
SET APPNAME=DLApplet
SET ZIP="C:\Program Files\7-zip\7z"
SET BUILDS=..\builds

FOR /F "TOKENS=1,2 DELIMS=/ " %%A IN ('DATE /T') DO SET mm=%%B
FOR /F "TOKENS=2,3 DELIMS=/ " %%A IN ('DATE /T') DO SET dd=%%B
FOR /F "TOKENS=3,4 DELIMS=/ " %%A IN ('DATE /T') DO SET yyyy=%%B

SET DATE=%yyyy%-%mm%-%dd%