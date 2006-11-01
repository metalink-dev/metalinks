#!/bin/sh
echo "This example needs metalink installed"
metalink --alldigests metalinks/itworked.png < sfmirrors > itworked.metalink

#Using MD5sum files
metalink --md5 MD5SUMS < ubuntumirrors > all_ubuntu_iso_files.metalink
