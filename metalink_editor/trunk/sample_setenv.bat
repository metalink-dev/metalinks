SET PYTHONDIR=c:\Python25
SET NSISDIR=C:\Program Files\NSIS
SET PYINSTALLERDIR=c:\pyinstaller_1.3\pyinstaller-1.3
SET PSCPDIR=c:\programme\PSCP
SET SFUSER=sourceforgenetuser

SET BUILDS=..\builds

FOR /F "TOKENS=1,2 DELIMS=/ " %%A IN ('DATE /T') DO SET mm=%%B
FOR /F "TOKENS=2,3 DELIMS=/ " %%A IN ('DATE /T') DO SET dd=%%B
FOR /F "TOKENS=3,4 DELIMS=/ " %%A IN ('DATE /T') DO SET yyyy=%%B

SET DATE=%yyyy%-%mm%-%dd%