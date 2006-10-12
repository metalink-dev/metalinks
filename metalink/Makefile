PREFIX=

.PHONY: all install
all: src/metalink

install: all 
	strip -s src/metalink
	mkdir -p $(PREFIX)/usr/bin
	mv src/metalink $(PREFIX)/usr/bin

clean: distclean

include Makefile.metalink
