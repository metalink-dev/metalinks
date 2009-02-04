call sample_setenv.bat
call setenv.bat

"%NSISDIR%\makensis.exe" setup.nsi

pause "done...hit a key to exit"