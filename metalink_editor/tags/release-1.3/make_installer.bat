call sample_setenv.bat
call setenv.bat

call py2exe.bat

"%NSISDIR%\makensis.exe" setup.nsi

echo "done..."