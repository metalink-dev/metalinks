#include "HashList.ih"

void HashList::finalize()
{
	_foreach(hash, *this)
		(*hash)->finalize();
}
