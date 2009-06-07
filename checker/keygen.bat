call sample_setenv.bat
call setenv.bat

"%JAVAPATH%\keytool.exe" -delete -alias %APPNAME%
"%JAVAPATH%\keytool.exe" -genkey -validity 365 -alias %APPNAME%
REM "%JAVAPATH%\keytool.exe" -export -alias %APPNAME%