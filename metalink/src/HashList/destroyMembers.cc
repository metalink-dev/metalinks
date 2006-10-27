#include "HashList.ih"
//TODO Indentation
		void HashList::destroyMembers()
		{
			_foreach(it, *this)
				delete *it;
		}
