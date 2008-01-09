@echo off
echo Building html documentation:
epydoc.py -v --html --name "Metalink Editor" --url "http://www.metamirrors.nl/metalink_editor" -o ../doc/epydoc/html ../src/metalink.py
rem echo Building pdf documentation:
rem epydoc.py -v --pdf --name "Metalink Editor" --url "http://www.metamirrors.nl/metalink_editor" -o ../doc/epydoc/pdf ../src/metalink.py