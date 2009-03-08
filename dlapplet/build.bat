call sample_setenv.bat
call setenv.bat

call clean.bat

REM "%JAVAPATH%\javac.exe" Download.java
"%JAVAPATH%\javac.exe" -Xlint:deprecation *.java
"%JAVAPATH%\jar.exe" cvf %APPNAME%.jar *.class
"%JAVAPATH%\jarsigner.exe" %APPNAME%.jar %APPNAME%
