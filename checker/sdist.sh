#!/bin/sh

python setup.py clean

# create the src .tar.gz
python setup.py sdist
