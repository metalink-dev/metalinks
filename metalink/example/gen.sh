#!/bin/sh
echo "This example needs metalink installed"
metalink --alldigests metalinks/itworked.png < sfmirrors > itworked.metalink

#Using MD5sum files
md5sum *.* > MD5SUMS
metalink --md5 MD5SUMS < example.com > frommd5.metalink
