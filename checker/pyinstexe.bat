rem *** Used to create a Python exe 

SET PYTHONDIR=c:\Python25
SET PYINSTALLERDIR=c:\pyinstaller_1.3\pyinstaller-1.3

SET BUILD=%PYINSTALLERDIR%\Build.py

SET PYTHONPATH=%PYTHONDIR%\python.exe

%PYTHONPATH% setup.py clean
%PYTHONPATH% setup.py merge

rem ***** create the exe
%PYTHONPATH% -OO %BUILD% metalink.spec

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"