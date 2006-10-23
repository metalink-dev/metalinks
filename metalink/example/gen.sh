#!/bin/sh
echo "This example needs metalink installed"
metalink --alldigests metalinks/itworked.png < sfmirrors > itworked.metalink

#Using MD5sum files
md5sum *.* > MD5SUMS
echo http http://example.com/|metalink --md5 MD5SUMS > frommd5.metalink
