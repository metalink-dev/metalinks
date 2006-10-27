#include "String.ih"
std::string String::translated(char from, char to)
{
				std::string copy(*this);
			_foreach(c, copy)
				if(*c == from)
					*c = to;
			return copy;

}
