../src/metalink --alldigests metalinks/itworked.png < sfmirrors > itworked.metalink

#Using MD5sum files
md5sum *.* > MD5SUMS
echo http http://example.com/|../src/metalink --md5 MD5SUMS > frommd5.metalink
