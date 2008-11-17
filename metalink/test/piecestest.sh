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
for i in 1 2 3 4 5 6 7 8 9; do dd if=/dev/urandom of=randomdata$i bs=32 count=8192
done
openssl sha1 randomdata*
echo ==
cat randomdata* > allrandom
../src/metalink --nomirrors -d sha1pieces allrandom |grep 'piece='
