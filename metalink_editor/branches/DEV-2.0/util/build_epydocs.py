#!/usr/bin/python
import os

build_html = True
build_pdf = True
doc_modules = ['metalink.py', 'test_metalink.py']

doc_modules_str = ''
for m in doc_modules:
  doc_modules_str += ' ../src/' + m

if build_html:
  print 'Building html docs:'
  os.system('epydoc.py -v --html --name "Metalink Editor" --url \
    "http://www.metamirrors.nl/metalink_editor" -o ../doc/epydoc/html' +
    doc_modules_str)
if build_pdf:
  print 'Building pdf docs:'
  os.system('epydoc.py -v --pdf --name "Metalink Editor" --url \
    "http://www.metamirrors.nl/metalink_editor" -o ../doc/epydoc/pdf' +
    doc_modules_str)