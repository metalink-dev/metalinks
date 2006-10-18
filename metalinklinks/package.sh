#!/bin/sh
ccbuild --nodefargs --args -O3 --addres src/ccResolutions makefile src/metalinklinks.cc > Makefile.metalinklinks
ccbuild --nodefargs --args -O3 --addres src/ccResolutions aap src/metalinklinks.cc > metalinklinks.aap

