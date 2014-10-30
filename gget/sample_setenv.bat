SET PSCPDIR=c:\programme\PSCP
SET SFUSER=sourceforgenetuser
SET BUILDS=..\builds
SET PATH=%PATH%;%PROGRAMFILES%\upx;%USERPROFILE%\downloads\development_tools\upx307w;%PROGRAMFILES(X86)%\NSIS;%PROGRAMFILES%\NSIS
SET PORTABLE=%USERPROFILE%\downloads\development_tools\PortableApps.comInstaller\PortableApps.comInstaller.exe
SET PYTHONDIR=D:\projects\Portable_Python_2.7.6.1\App

FOR /F "TOKENS=1,2 DELIMS=/ " %%A IN ('DATE /T') DO SET mm=%%B
FOR /F "TOKENS=2,3 DELIMS=/ " %%A IN ('DATE /T') DO SET dd=%%B
FOR /F "TOKENS=3,4 DELIMS=/ " %%A IN ('DATE /T') DO SET yyyy=%%B

SET MYDATE=%yyyy%-%mm%-%dd%

IF NOT EXIST setenv.bat GOTO NOSETENV
   call setenv.bat
:NOSETENV

