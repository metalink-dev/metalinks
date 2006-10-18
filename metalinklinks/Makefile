PREFIX=

.PHONY: all install
all: src/metalinklinks

install: all 
	strip -s src/metalinklinks
	mkdir -p $(PREFIX)/usr/bin
	mv src/metalinklinks $(PREFIX)/usr/bin

clean: distclean

include Makefile.metalinklinks
