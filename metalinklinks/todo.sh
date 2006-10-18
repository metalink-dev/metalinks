#!/bin/sh

#List source code //TODO's
#
#
grep -R -o "//TODO.*$" src/* | awk -- 'BEGIN{FS=":";}//{ if(last!=$1) {print $1; last=$1 } print "   " substr($0, index($0,":") +1);}'
