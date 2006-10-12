
#Generate the stylesheet variable from the monolithic XSLT file given as argument
echo '#include "Globals.ih"' > stylesheet.cc
echo "std::string Globals::stylesheet(\"\\" >> stylesheet.cc
sed -e 's/"/\\"/g' -e 's/$/\\n\t\\/' < $1 >> stylesheet.cc
echo '");' >> stylesheet.cc

