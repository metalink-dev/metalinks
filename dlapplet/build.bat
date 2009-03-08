call sample_setenv.bat
call setenv.bat

call clean.bat

"%JAVAPATH%\javac.exe" -Xlint:unchecked *.java
"%JAVAPATH%\jar.exe" cvf %APPNAME%.jar *.class
"%JAVAPATH%\jarsigner.exe" %APPNAME%.jar %APPNAME%
