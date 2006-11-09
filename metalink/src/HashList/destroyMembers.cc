#include "HashList.ih"

void HashList::destroyMembers()
{
	_foreach(it, *this)
		delete *it;
}
