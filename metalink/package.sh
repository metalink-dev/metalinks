#!/bin/sh
# Makefile support has been dropped in favor of GNU autotools support
sh bootstrap
ccbuild --nodefargs --args "-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE" --addres src/ccResolutions makefile src/metalink.cc > Makefile.metalink
ccbuild --nodefargs --args "-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE" --addres src/ccResolutions aap src/metalink.cc > metalink.aap

