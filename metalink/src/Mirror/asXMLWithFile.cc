#include "Mirror.ih"

std::string Mirror::asXMLWithFile(std::string const &file) const
{
	ostringstream out;
	out << "<url";

	//Attributes	
	if(d_preference > 0)
		out << " preference=\"" << d_preference << "\"";
	if(d_location.length() > 0)
		out << " location=\"" << d_location << "\"";
	if(d_type.length() > 0)
		out << " type=\"" << d_type << "\"";

	//Close opening tag
	out << ">";
	//content
	out << d_path << Globals::XMLSafe(file);
	
	//Closing tag
	out << "</url>";
	return out.str();
}
