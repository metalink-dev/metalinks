rem *** Used to create a Python .zip

call sample_setenv.bat

setup.py clean

rem ***** create the .zip
setup.py sdist

echo "done..."