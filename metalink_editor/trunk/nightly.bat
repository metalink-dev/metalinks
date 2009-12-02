call sample_setenv.bat
call setenv.bat

mkdir "%BUILDS%"

call sdist.bat
xcopy /Y "dist\Metalink Editor-*.zip" "%BUILDS%\."
move "%BUILDS%\Metalink Editor-*.zip" "%BUILDS%\%DATE%_Metalink_Editor.zip"
call make_installer.bat
xcopy /Y "Metalink Editor-*-win32.zip" "%BUILDS%\."
move "%BUILDS%\Metalink Editor-*-win32.zip" "%BUILDS%\%DATE%_Metalink_Editor-win32.zip"
xcopy /Y "Metalink Editor-*.exe" "%BUILDS%\."
move "%BUILDS%\Metalink Editor-*.exe" "%BUILDS%\%DATE%_Metalink_Editor.exe"
