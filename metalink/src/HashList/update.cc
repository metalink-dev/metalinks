#include "HashList.ih"
//TODO Indentation
		void HashList::update(char const *bytes, unsigned numbytes)
		{
			_foreach(hash, *this)
				(*hash)->update(bytes, numbytes);
		}
