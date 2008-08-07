#include "String.ih"
void String::toUpper()
{
	transform(this->begin(), this->end(), this->begin(), static_cast<int (*)(int)>(std::toupper));	
}
