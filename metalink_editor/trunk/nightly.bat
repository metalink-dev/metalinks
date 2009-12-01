call sample_setenv.bat
call setenv.bat

mkdir "%BUILDS%"

call sdist.bat
xcopy /Y "dist\*.zip" "%BUILDS%\."
move "%BUILDS%\*.zip" "%BUILDS%\%DATE%_Metalink_Editor.zip"
call make_installer.bat
xcopy /Y "*-win32.zip" "%BUILDS%\."
move "%BUILDS%\*-win32.zip" "%BUILDS%\%DATE%_Metalink_Editor-win32.zip"
xcopy /Y "Metalink Editor-*.exe" "%BUILDS%\."
move "%BUILDS%\Metalink Editor-*.exe" "%BUILDS%\%DATE%_Metalink_Editor.exe"
