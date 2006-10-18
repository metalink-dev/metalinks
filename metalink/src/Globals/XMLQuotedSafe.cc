#include "Globals.ih"

std::string Globals::XMLQuotedSafe(std::string value)
{
	//TODO Quote thingies: " -> &quot;
	return XMLSafe(value);
}
