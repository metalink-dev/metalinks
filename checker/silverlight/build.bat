SET PYTHONLIB=c:\python26\lib

xcopy /Y %PYTHONLIB%\*.py src\.

Chiron /d:src /z:app.xap

del app.xap

cd src

"C:\Program Files\7-Zip\7z.exe" a -r -tzip -xr!*.svn* ..\app.xap .

cd ..

echo Build complete.

pause