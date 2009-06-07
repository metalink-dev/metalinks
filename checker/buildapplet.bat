@ECHO ON

set JYTHON_HOME="c:\jython2.5rc3"
set JAVA_HOME="C:\Program Files\Java\jdk1.6.0_12"
set BUILD_DIR=build

call %JYTHON_HOME%\jython.bat setup.py clean

mkdir %BUILD_DIR%

copy %JYTHON_HOME%\jython.jar %BUILD_DIR%\.

cd jyinterface
%JAVA_HOME%\bin\javac.exe -classpath %JYTHON_HOME%\jython.jar Download.java JythonFactory.java Main.java DLApplet.java
mkdir ..\%BUILD_DIR%\jyinterface
mv *.class ..\%BUILD_DIR%\jyinterface
cd ..

xcopy /S %JYTHON_HOME%\Lib\* %BUILD_DIR%\.

copy download.py %BUILD_DIR%\.
copy xmlutils.py %BUILD_DIR%\.

cd %BUILD_DIR%
echo Class-Path: jython.jar > manifest.txt
%JAVA_HOME%\bin\jar.exe cvfme DLApplet.jar manifest.txt jyinterface.Main *

REM %JAVA_HOME%\bin\java.exe -jar applet.jar

cd ..

pause
