call sample_setenv.bat
call setenv.bat

call py2exe.bat

"%NSISDIR%\makensis.exe" setup.nsi

pause "done...hit a key to exit"