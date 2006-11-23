for i in 1 2 3 4 5 6 7 8 9; do dd if=/dev/urandom of=randomdata$i bs=32 count=4096
done
openssl sha1 randomdata*
echo ==
cat randomdata* > allrandom
../src/metalink --nomirrors allrandom |grep 'piece='
