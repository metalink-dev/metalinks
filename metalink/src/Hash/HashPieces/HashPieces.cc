#include "HashPieces.ih"
HashPieces::HashPieces(unsigned int size)
		:
		d_size(size),
		d_count(0),
		d_h(new GCrypt(GCRY_MD_SHA1))
{
}
