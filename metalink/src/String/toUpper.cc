#include "String.ih"
void String::toUpper()
{
	transform(this->begin(), this->end(), this->begin(), toupper);	
}
