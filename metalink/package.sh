#!/bin/sh
ccbuild --nodefargs --args -O2 --addres src/ccResolutions makefile src/metalink.cc > Makefile.metalink
ccbuild --nodefargs --args -O2 --addres src/ccResolutions aap src/metalink.cc > metalink.aap

