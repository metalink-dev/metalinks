#include "HashPieces.ih"
HashPieces::HashPieces(unsigned long long size)
		:
		d_size(size),
		d_count(0),
		d_h(new GCrypt(GCRY_MD_SHA1))
{
}
