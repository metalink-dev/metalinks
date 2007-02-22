#!/bin/sh
ccbuild --nodefargs --args "-O2 -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE" --addres src/ccResolutions makefile src/metalink.cc > Makefile.metalink
ccbuild --nodefargs --args "-O2 -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE" --addres src/ccResolutions aap src/metalink.cc > metalink.aap

