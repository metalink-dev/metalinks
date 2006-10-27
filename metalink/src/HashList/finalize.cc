#include "HashList.ih"
//TODO Indentation
		void HashList::finalize()
		{
			_foreach(hash, *this)
				(*hash)->finalize();
				}
