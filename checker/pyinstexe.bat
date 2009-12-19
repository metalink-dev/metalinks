rem *** Used to create a Python exe 

call sample_setenv.bat
call setenv.bat

SET BUILD=%PYINSTALLERDIR%\Build.py

SET PYTHONPATH=%PYTHONDIR%\python.exe

%PYTHONPATH% setup.py clean
%PYTHONPATH% setup.py merge

rem ***** create the exe
%PYTHONPATH% -OO %BUILD% metalink.spec
%PYTHONPATH% -OO %BUILD% metalinkw.spec

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"