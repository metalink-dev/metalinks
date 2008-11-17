#!/bin/sh
#
#  This file is part of the metalink program
#  Copyright (C) 2008  A. Bram Neijt <bneijt@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#Bash/AWK script to create separate metalink files per MD5SUM entry
#A) You must have metalink in your PATH (try: metalink --help)
#B) Usage: sh ./separatemd5.sh MD5SUMS sfmirrors

awk -- 'BEGIN{tmpfile="/tmp/metamd5tmp.tmp";}//{print($0) > tmpfile; filename=$2;gsub(/\./, "_", filename); filename=filename "_md5.metalink"; close(tmpfile); system("metalink --md5 " tmpfile " < '$2' > " filename)}' < $1
