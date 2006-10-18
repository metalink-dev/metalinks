
#Bash/AWK script to create separate metalink files per MD5SUM entry
#A) You must have metalink in your PATH (try: metalink --help)
#B) Usage: sh ./separatemd5.sh MD5SUMS sfmirrors

awk -- 'BEGIN{tmpfile="/tmp/metamd5tmp.tmp";}//{print($0) > tmpfile; filename=$2;gsub(/\./, "_", filename); filename=filename "_md5.metalink"; close(tmpfile); system("metalink --md5 " tmpfile " < '$2' > " filename)}' < $1
