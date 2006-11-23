#include "Hash.ih"

std::string Hash::xml() const
{

	std::ostringstream v;
 	v << "<hash type=\"" << this->name() << "\">"
 			<< this->value()
 			<< "</hash>";
	return v.str();
}
