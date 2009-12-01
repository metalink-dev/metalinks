rem *** Used to create a Python .zip

call sample_setenv.bat
call setenv.bat

SET PYTHONPATH=%PYTHONDIR%\python.exe

%PYTHONPATH% setup.py clean

rem ***** create the .zip
%PYTHONPATH% setup.py sdist

echo "done..."