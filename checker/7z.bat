SET NAME=build

:: 7-zip self installer
cd %NAME%

"%PROGRAMFILES(x86)%\7-Zip\7z" a -t7z ..\%NAME%.7z *
cd ..

copy /b 7zS.sfx + 7z.txt + %NAME%.7z %NAME%.exe
move %NAME%.exe metalinkc.exe
