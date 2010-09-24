#!/bin/sh

PYDIR=/usr/lib/python2.5/

# Optimized
#MODULES="copy httplib gzip types struct mimetools os ntpath stat rfc822 tempfile random warnings BaseHTTPServer linecache gettext"

rm -rf app.xap

cd src

# The lazy way
for module in $PYDIR*.py; do
    cp $module .
done

#for module in $MODULES; do
#    cp $PYDIR$module.py .
#done

zip -9 -r ../app.xap * -x \*.svn\*

cd ..
