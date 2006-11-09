#include "HashList.ih"

void HashList::update(char const *bytes, unsigned numbytes)
{
	_foreach(hash, *this)
		(*hash)->update(bytes, numbytes);
}
