rem *** Used to create a Python exe 

call sample_setenv.bat
call setenv.bat

SET PYTHONPATH=%PYTHONDIR%\python.exe

%PYTHONPATH% setup.py clean

rem ***** create the exe
%PYTHONPATH% -OO setup.py py2exe 
rem --packages=libappupdater

%PYTHONPATH% setup.py zip

echo "done..."